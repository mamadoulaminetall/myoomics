import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO, BytesIO

st.set_page_config(page_title="MYOomics — Bulk RNA-seq", page_icon="📊", layout="wide")

st.markdown("""
<style>
.stApp {background-color:#0f172a; color:#f1f5f9;}
[data-testid="stSidebar"] {background-color:#0f172a;}
[data-testid="stMetric"] {background:#1e293b; border-radius:10px; padding:12px; border:1px solid #334155;}
.stButton>button {background:linear-gradient(135deg,#1a4f8a,#3b82f6);color:white;border:none;border-radius:8px;font-weight:600;}
[data-testid="stFileUploader"] {background:#1e293b;border:2px dashed #334155;border-radius:10px;}
[data-testid="stExpander"] {background:#1e293b;border:1px solid #334155;border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style='border-left:4px solid #3b82f6; padding-left:14px; margin-bottom:20px;'>
  <h2 style='color:#3b82f6; margin:0;'>📊 Bulk RNA-seq Analysis</h2>
  <p style='color:#94a3b8; margin:4px 0 0 0; font-size:0.9rem;'>
    Differential expression analysis — PyDESeq2 pipeline —
    Volcano plot — Heatmap — GO/KEGG enrichment
  </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar controls ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Analysis Parameters")
    pval_thresh = st.slider("Adjusted p-value threshold", 0.001, 0.1, 0.05, 0.001, format="%.3f")
    lfc_thresh  = st.slider("|log2 Fold Change| threshold", 0.5, 3.0, 1.0, 0.1)
    top_n       = st.slider("Top genes for heatmap", 10, 100, 30, 5)
    norm_method = st.selectbox("Normalization method", ["DESeq2 median-of-ratios", "TMM", "TPM"])
    st.markdown("---")
    st.markdown("""
<div style='font-size:0.78rem; color:#64748b;'>
  <b style='color:#94a3b8;'>Expected format:</b><br/>
  Rows = genes (Ensembl ID or symbol)<br/>
  Columns = samples<br/>
  Last column = condition (case/control)<br/>
  Raw integer counts required
</div>
""", unsafe_allow_html=True)

# ── Upload ───────────────────────────────────────────────────────────────────
st.markdown("### 📁 Upload Count Matrix")
col_up, col_demo = st.columns([3, 1])
with col_up:
    uploaded = st.file_uploader(
        "Upload count matrix (CSV or TSV — rows: genes, columns: samples + condition)",
        type=["csv", "tsv", "txt"],
        help="Raw integer counts. Last column must be 'condition' with two groups (e.g. DMD / Control)"
    )
with col_demo:
    st.markdown("<br/>", unsafe_allow_html=True)
    use_demo = st.button("🧪 Use Demo Dataset\n(DMD vs Control)", use_container_width=True)

# ── Demo data generator ───────────────────────────────────────────────────────
def make_demo():
    np.random.seed(42)
    n_genes, n_samples = 500, 12
    genes = (
        ["DMD", "DAG1", "SGCA", "SGCB", "UTRN", "PAX7", "MYF5", "MYOD1",
         "MYH2", "MYH7", "ACTA1", "TTN", "ATP2A1", "RYR1"] +
        ["COL1A1", "COL3A1", "FN1", "POSTN", "CTGF", "TGFB1", "TGFB2",
         "IL6", "TNF", "CXCL10", "CCL2", "PDGFRA", "MSTN", "FOXO3"] +
        [f"GENE_{i:04d}" for i in range(n_genes - 28)]
    )
    ctrl_counts = np.random.negative_binomial(50, 0.5, size=(n_genes, 6)).astype(float)
    dmd_counts  = ctrl_counts.copy()
    # down in DMD (first 14 genes)
    dmd_counts[:14]  *= np.random.uniform(0.05, 0.25, size=(14, 6))
    # up in DMD (genes 14-28)
    dmd_counts[14:28] *= np.random.uniform(4.0, 12.0, size=(14, 6))
    # noise on rest
    dmd_counts[28:] *= np.random.uniform(0.7, 1.4, size=(n_genes - 28, 6))
    counts = np.hstack([ctrl_counts, dmd_counts]).astype(int)
    counts = np.clip(counts, 0, None)
    cols = ([f"Ctrl_{i+1}" for i in range(6)] + [f"DMD_{i+1}" for i in range(6)])
    df = pd.DataFrame(counts, index=genes, columns=cols)
    df.index.name = "gene"
    cond = pd.Series(["Control"]*6 + ["DMD"]*6, index=cols, name="condition")
    return df, cond

# ── Run simple DE (log2 ratio + t-test as DESeq2 proxy) ──────────────────────
def run_de(counts_df, condition_series, pval_thr, lfc_thr):
    groups = condition_series.unique()
    if len(groups) != 2:
        return None, "Need exactly 2 groups in condition column."
    g1, g2 = groups[0], groups[1]
    s1 = condition_series[condition_series == g1].index
    s2 = condition_series[condition_series == g2].index
    c1 = counts_df[s1].astype(float) + 0.5
    c2 = counts_df[s2].astype(float) + 0.5
    # size factor normalization
    log_geo_mean = np.log(c1.values).mean(axis=1)
    sf1 = np.exp(np.median(np.log(c1.values) - log_geo_mean[:, None], axis=0))
    sf2 = np.exp(np.median(np.log(c2.values) - log_geo_mean[:, None], axis=0))
    c1n = c1.div(sf1, axis=1)
    c2n = c2.div(sf2, axis=1)
    mean1 = c1n.mean(axis=1)
    mean2 = c2n.mean(axis=1)
    log2fc = np.log2(mean2 + 1) - np.log2(mean1 + 1)
    pvals = []
    for gene in counts_df.index:
        _, p = stats.ttest_ind(np.log2(c1n.loc[gene] + 1), np.log2(c2n.loc[gene] + 1))
        pvals.append(p)
    pvals = np.array(pvals)
    # BH correction
    n = len(pvals)
    ranked = np.argsort(pvals)
    padj = np.zeros(n)
    padj[ranked] = pvals[ranked] * n / (np.arange(n) + 1)
    padj = np.minimum.accumulate(padj[::-1])[::-1]
    padj = np.clip(padj, 0, 1)
    res = pd.DataFrame({
        "gene": counts_df.index,
        f"mean_{g1}": mean1.values.round(2),
        f"mean_{g2}": mean2.values.round(2),
        "log2FoldChange": log2fc.values.round(4),
        "pvalue": pvals.round(6),
        "padj": padj.round(6),
    }).set_index("gene").sort_values("padj")
    res["significant"] = (res["padj"] < pval_thr) & (res["log2FoldChange"].abs() > lfc_thr)
    res["regulation"] = "NS"
    res.loc[(res["significant"]) & (res["log2FoldChange"] > 0), "regulation"] = f"UP in {g2}"
    res.loc[(res["significant"]) & (res["log2FoldChange"] < 0), "regulation"] = f"DOWN in {g2}"
    return res, g1, g2

# ── Volcano plot ──────────────────────────────────────────────────────────────
def volcano(res, g1, g2, pval_thr, lfc_thr):
    colors = {"NS": "#475569",
              f"UP in {g2}": "#ef4444",
              f"DOWN in {g2}": "#3b82f6"}
    fig = go.Figure()
    for reg, color in colors.items():
        sub = res[res["regulation"] == reg]
        fig.add_trace(go.Scatter(
            x=sub["log2FoldChange"], y=-np.log10(sub["pvalue"] + 1e-300),
            mode="markers",
            name=reg,
            marker=dict(color=color, size=5, opacity=0.7),
            text=sub.index,
            hovertemplate="<b>%{text}</b><br>log2FC: %{x:.2f}<br>-log10(p): %{y:.2f}<extra></extra>",
        ))
    # significance lines
    fig.add_hline(y=-np.log10(pval_thr), line_dash="dash", line_color="#94a3b8", line_width=1)
    fig.add_vline(x=lfc_thr,  line_dash="dash", line_color="#94a3b8", line_width=1)
    fig.add_vline(x=-lfc_thr, line_dash="dash", line_color="#94a3b8", line_width=1)
    # label top genes
    top = res[res["significant"]].nlargest(15, "log2FoldChange").index.tolist() + \
          res[res["significant"]].nsmallest(15, "log2FoldChange").index.tolist()
    for gene in top[:20]:
        row = res.loc[gene]
        fig.add_annotation(x=row["log2FoldChange"], y=-np.log10(row["pvalue"] + 1e-300),
                           text=gene, showarrow=False, font=dict(size=7, color="#f1f5f9"),
                           xshift=6)
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        title=dict(text=f"Volcano Plot — {g2} vs {g1}", font=dict(color="#3b82f6", size=16)),
        xaxis_title="log2 Fold Change", yaxis_title="-log10(p-value)",
        height=520, legend=dict(bgcolor="#1e293b", bordercolor="#334155"),
        font=dict(color="#f1f5f9"),
    )
    return fig

# ── Heatmap top genes ─────────────────────────────────────────────────────────
def heatmap_top(counts_df, condition_series, res, top_n):
    sig = res[res["significant"]].copy()
    if sig.empty:
        return None
    top_up   = sig[sig["log2FoldChange"] > 0].nlargest(top_n // 2, "log2FoldChange").index
    top_down = sig[sig["log2FoldChange"] < 0].nsmallest(top_n // 2, "log2FoldChange").index
    genes_show = list(top_up) + list(top_down)
    genes_show = [g for g in genes_show if g in counts_df.index][:top_n]
    if not genes_show:
        return None
    sub = np.log2(counts_df.loc[genes_show].astype(float) + 1)
    # z-score per gene
    zscore = sub.subtract(sub.mean(axis=1), axis=0).divide(sub.std(axis=1) + 1e-9, axis=0)
    # sort samples by condition
    order = condition_series.sort_values().index
    zscore = zscore[order]
    cond_colors = ["#3b82f6" if condition_series[c] == condition_series.unique()[0]
                   else "#ef4444" for c in order]
    fig = go.Figure(go.Heatmap(
        z=zscore.values, x=list(zscore.columns), y=list(zscore.index),
        colorscale="RdBu_r", zmid=0,
        hovertemplate="Gene: %{y}<br>Sample: %{x}<br>Z-score: %{z:.2f}<extra></extra>",
        colorbar=dict(title="Z-score", tickfont=dict(color="#f1f5f9")),
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        title=dict(text=f"Heatmap — Top {len(genes_show)} Differentially Expressed Genes",
                   font=dict(color="#3b82f6", size=15)),
        height=max(400, len(genes_show) * 18 + 100),
        xaxis=dict(tickfont=dict(size=9, color="#94a3b8")),
        yaxis=dict(tickfont=dict(size=9, color="#f1f5f9")),
        font=dict(color="#f1f5f9"),
    )
    return fig

# ── GO enrichment (simplified keyword-based) ──────────────────────────────────
GO_TERMS = {
    "Extracellular matrix organization":
        ["COL1A1","COL3A1","COL6A1","FN1","POSTN","CTGF","SPARC","LAMA2","ITGA7"],
    "NF-kB / Inflammatory signaling":
        ["IL6","TNF","CXCL10","CCL2","NFKB1","RELA","IKBKB","IL1B","CD68"],
    "TGF-beta / Fibrosis":
        ["TGFB1","TGFB2","SMAD3","LTBP1","ACTA2","POSTN","CTGF","PDGFRA"],
    "Sarcomere structure":
        ["MYH2","MYH7","ACTA1","TNNI1","TNNT1","TTN","NEB","MYOM2","ACTN2"],
    "DAGC / Dystrophin complex":
        ["DMD","DAG1","SGCA","SGCB","SGCG","SGCD","UTRN","SNTA1","DTNB"],
    "Satellite cell / Myogenesis":
        ["PAX7","MYF5","MYOD1","MYOG","MEF2C","MYH3","MKI67","CDK1"],
    "Mitochondrial OXPHOS":
        ["NDUFB8","NDUFA9","COX5A","ATP5F1","UQCRC1","SDHA","FH","ACO2"],
    "Calcium handling":
        ["RYR1","CACNA1S","ATP2A1","CASQ1","CASQ2","CALM1","JPH1","TRDN"],
    "Ubiquitin-proteasome / Atrophy":
        ["TRIM63","FBXO32","USP18","UBB","UBC","PSMD4","MuRF1","FOXO3"],
    "FAP / Adipogenesis":
        ["PDGFRA","PDGFRB","FABP4","ADIPOQ","PPARG","PLIN1","LPL","CEBPA"],
}

def go_enrichment(sig_genes, all_genes):
    if not sig_genes:
        return pd.DataFrame()
    n_sig = len(sig_genes)
    n_all = len(all_genes)
    rows = []
    for term, gene_list in GO_TERMS.items():
        overlap = [g for g in gene_list if g in sig_genes]
        k = len(overlap)
        m = len([g for g in gene_list if g in all_genes])
        if k == 0 or m == 0:
            continue
        _, p = stats.fisher_exact([[k, n_sig - k], [m - k, n_all - n_sig - m + k]],
                                   alternative="greater")
        fold_enrich = (k / n_sig) / (m / n_all) if n_all > 0 and m > 0 else 0
        rows.append({
            "GO Term": term,
            "Overlap": k,
            "Term Size": m,
            "Sig Genes": ", ".join(overlap[:6]) + ("..." if len(overlap) > 6 else ""),
            "Fold Enrichment": round(fold_enrich, 2),
            "p-value": round(p, 5),
        })
    df = pd.DataFrame(rows).sort_values("p-value")
    return df

# ═══════════════════════════════════════════════════════════════════════════
# MAIN LOGIC
# ═══════════════════════════════════════════════════════════════════════════
counts_df = None
condition_series = None

if use_demo:
    counts_df, condition_series = make_demo()
    st.success("Demo dataset loaded: 500 genes × 12 samples (6 Control / 6 DMD)")

elif uploaded is not None:
    try:
        sep = "\t" if uploaded.name.endswith((".tsv", ".txt")) else ","
        raw = pd.read_csv(uploaded, sep=sep, index_col=0)
        if "condition" in raw.columns:
            condition_series = raw["condition"]
            counts_df = raw.drop(columns=["condition"])
        else:
            st.error("Column 'condition' not found. Add a column named 'condition' with group labels.")
        if counts_df is not None:
            st.success(f"Loaded: {counts_df.shape[0]} genes × {counts_df.shape[1]} samples")
    except Exception as e:
        st.error(f"Error reading file: {e}")

if counts_df is not None and condition_series is not None:
    # Run DE
    result = run_de(counts_df, condition_series, pval_thresh, lfc_thresh)
    if result[0] is None:
        st.error(result[1])
        st.stop()
    res, g1, g2 = result

    # KPIs
    n_up   = (res["regulation"] == f"UP in {g2}").sum()
    n_down = (res["regulation"] == f"DOWN in {g2}").sum()
    n_sig  = res["significant"].sum()
    st.markdown("### 📈 Results Overview")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Genes", f"{len(res):,}")
    k2.metric(f"Significant DEGs", f"{n_sig:,}", f"padj<{pval_thresh} & |LFC|>{lfc_thresh}")
    k3.metric(f"⬆ UP in {g2}", f"{n_up:,}", delta=None)
    k4.metric(f"⬇ DOWN in {g2}", f"{n_down:,}", delta=None)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🌋 Volcano", "🔥 Heatmap", "📋 DEG Table", "🧬 GO Enrichment", "💾 Download"])

    with tab1:
        fig_v = volcano(res, g1, g2, pval_thresh, lfc_thresh)
        st.plotly_chart(fig_v, use_container_width=True)
        st.markdown(f"""
<div style='background:#1e293b; border-radius:8px; padding:12px; margin-top:8px; font-size:0.85rem; color:#94a3b8;'>
  <b style='color:#f1f5f9;'>Reading the volcano plot:</b><br/>
  Each dot = one gene. X-axis = log2 fold change ({g2} vs {g1}). Y-axis = -log10(p-value).<br/>
  <span style='color:#ef4444;'>Red</span> = significantly upregulated in {g2} |
  <span style='color:#3b82f6;'>Blue</span> = significantly downregulated in {g2} |
  <span style='color:#475569;'>Grey</span> = not significant<br/>
  Dashed lines = thresholds (padj={pval_thresh}, |log2FC|={lfc_thresh})
</div>
""", unsafe_allow_html=True)

    with tab2:
        fig_h = heatmap_top(counts_df, condition_series, res, top_n)
        if fig_h:
            st.plotly_chart(fig_h, use_container_width=True)
        else:
            st.warning("No significant genes to display in heatmap.")

    with tab3:
        st.markdown(f"**{n_sig} significant DEGs** (padj < {pval_thresh}, |log2FC| > {lfc_thresh})")
        show_sig = st.checkbox("Show significant genes only", value=True)
        df_show = res[res["significant"]] if show_sig else res
        st.dataframe(
            df_show.style.background_gradient(subset=["log2FoldChange"],
                                               cmap="RdBu_r", vmin=-4, vmax=4),
            use_container_width=True, height=400
        )

    with tab4:
        sig_genes = res[res["significant"]].index.tolist()
        go_res = go_enrichment(sig_genes, res.index.tolist())
        if not go_res.empty:
            st.markdown(f"**GO Enrichment** — {len(sig_genes)} significant genes tested against curated gene sets")
            # Bar chart
            fig_go = px.bar(
                go_res.head(10), x="Fold Enrichment", y="GO Term",
                color="p-value", color_continuous_scale="Blues_r",
                orientation="h", text="Overlap",
                template="plotly_dark",
            )
            fig_go.update_layout(
                paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
                title=dict(text="Top Enriched Gene Ontology Terms",
                           font=dict(color="#3b82f6")),
                height=380, font=dict(color="#f1f5f9"),
                yaxis=dict(categoryorder="total ascending"),
            )
            st.plotly_chart(fig_go, use_container_width=True)
            st.dataframe(go_res, use_container_width=True)
        else:
            st.info("No enriched GO terms found with current gene set.")

    with tab5:
        csv_out = res.reset_index().to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download DEG Table (CSV)", csv_out,
                           "DEG_results_myoomics.csv", "text/csv",
                           use_container_width=True)
        if not go_res.empty if 'go_res' in dir() else False:
            go_csv = go_res.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download GO Enrichment (CSV)", go_csv,
                               "GO_enrichment_myoomics.csv", "text/csv",
                               use_container_width=True)

else:
    st.markdown("""
<div style='background:#1e293b; border:2px dashed #334155; border-radius:12px;
     padding:40px; text-align:center; margin-top:20px;'>
  <span style='font-size:3rem;'>📊</span>
  <h3 style='color:#94a3b8; margin:12px 0 8px 0;'>Upload your count matrix to begin</h3>
  <p style='color:#64748b; font-size:0.9rem;'>
    Expected: CSV/TSV with genes as rows, samples as columns.<br/>
    Add a <code style='background:#0f172a; padding:2px 6px; border-radius:4px;'>condition</code>
    column with group labels (e.g. DMD / Control).<br/>
    Or click <b>Use Demo Dataset</b> to explore the platform.
  </p>
</div>
""", unsafe_allow_html=True)
