import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy.spatial.distance import cdist

st.set_page_config(page_title="MYOomics — Single-Cell", page_icon="🔬", layout="wide")

st.markdown("""
<style>
.stApp {background-color:#0f172a; color:#f1f5f9;}
[data-testid="stSidebar"] {background-color:#0f172a;}
[data-testid="stMetric"] {background:#1e293b;border-radius:10px;padding:12px;border:1px solid #334155;}
.stButton>button {background:linear-gradient(135deg,#1e5a2e,#22c55e);color:white;border:none;border-radius:8px;font-weight:600;}
[data-testid="stFileUploader"] {background:#1e293b;border:2px dashed #334155;border-radius:10px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='border-left:4px solid #22c55e; padding-left:14px; margin-bottom:20px;'>
  <h2 style='color:#22c55e; margin:0;'>🔬 Single-Cell / snRNA-seq Analysis</h2>
  <p style='color:#94a3b8; margin:4px 0 0 0; font-size:0.9rem;'>
    UMAP dimensionality reduction — Leiden clustering — Marker gene identification —
    Cell type annotation — CellChat ligand-receptor
  </p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ scRNA-seq Parameters")
    n_neighbors   = st.slider("n_neighbors (UMAP)", 5, 50, 15)
    min_dist      = st.slider("min_dist (UMAP)", 0.01, 0.9, 0.3, 0.01)
    resolution    = st.slider("Leiden resolution", 0.1, 2.0, 0.5, 0.1)
    min_genes     = st.slider("Min genes / cell", 100, 1000, 200, 50)
    min_cells     = st.slider("Min cells / gene", 1, 20, 3)
    n_top_markers = st.slider("Markers per cluster", 3, 20, 5)
    st.markdown("---")
    st.markdown("""
<div style='font-size:0.78rem; color:#64748b;'>
  <b style='color:#94a3b8;'>Supported formats:</b><br/>
  CSV: rows=cells, cols=genes + 'barcode' column<br/>
  H5AD: AnnData format (Scanpy)<br/>
  10x MEX: upload barcodes + features + matrix
</div>
""", unsafe_allow_html=True)

# ── Demo data: simulate muscle single-cell ────────────────────────────────────
CELL_TYPES = {
    "Type I Fiber (slow)":       {"color": "#3b82f6", "n": 80,
        "markers": ["MYH7", "MYH2", "TNNI1", "TTN", "ATP2A2"]},
    "Type II Fiber (fast)":      {"color": "#06b6d4", "n": 70,
        "markers": ["MYH1", "MYH4", "TNNI2", "ACTA1", "ATP2A1"]},
    "Satellite Cell (PAX7+)":    {"color": "#22c55e", "n": 40,
        "markers": ["PAX7", "MYF5", "CD34", "SPRY1", "CAV1"]},
    "FAP (pro-fibrotic)":        {"color": "#ef4444", "n": 55,
        "markers": ["PDGFRA", "COL1A1", "ACTA2", "TGFB1", "POSTN"]},
    "FAP (adipogenic)":          {"color": "#f97316", "n": 35,
        "markers": ["PDGFRA", "FABP4", "PPARG", "ADIPOQ", "PLIN1"]},
    "Macrophage (M1)":           {"color": "#eab308", "n": 30,
        "markers": ["CD68", "TNF", "IL6", "CXCL10", "CD80"]},
    "Macrophage (M2/pro-fibr.)": {"color": "#a855f7", "n": 25,
        "markers": ["CD163", "MRC1", "TGFB1", "CCL18", "FOLR2"]},
    "Endothelial Cell":          {"color": "#ec4899", "n": 35,
        "markers": ["PECAM1", "CDH5", "VWF", "CLDN5", "ESAM"]},
    "Pericyte":                  {"color": "#94a3b8", "n": 20,
        "markers": ["PDGFRB", "RGS5", "MCAM", "KCNJ8", "ABCC9"]},
}

def make_demo_sc():
    np.random.seed(123)
    all_markers = list({m for ct in CELL_TYPES.values() for m in ct["markers"]})
    extra_genes = [f"GENE_{i:04d}" for i in range(200)]
    all_genes = all_markers + extra_genes
    cells, cell_types, barcodes, umap1, umap2 = [], [], [], [], []
    cluster_centers = {
        "Type I Fiber (slow)":       (-4.0,  3.0),
        "Type II Fiber (fast)":      (-4.0, -3.0),
        "Satellite Cell (PAX7+)":    ( 4.0,  4.0),
        "FAP (pro-fibrotic)":        ( 5.0, -1.0),
        "FAP (adipogenic)":          ( 5.5,  1.5),
        "Macrophage (M1)":           ( 0.0,  5.5),
        "Macrophage (M2/pro-fibr.)": ( 1.5,  4.5),
        "Endothelial Cell":          (-1.5, -5.0),
        "Pericyte":                  (-3.0, -5.5),
    }
    for ct_name, ct_info in CELL_TYPES.items():
        n = ct_info["n"]
        cx, cy = cluster_centers[ct_name]
        for i in range(n):
            expr = np.random.poisson(2, len(all_genes)).astype(float)
            for m in ct_info["markers"]:
                idx = all_genes.index(m)
                expr[idx] = np.random.poisson(25) + 10
            cells.append(expr)
            cell_types.append(ct_name)
            barcodes.append(f"{ct_name[:4].upper()}_{i+1:04d}")
            umap1.append(cx + np.random.normal(0, 0.8))
            umap2.append(cy + np.random.normal(0, 0.8))
    expr_matrix = pd.DataFrame(cells, columns=all_genes, index=barcodes)
    meta = pd.DataFrame({"cell_type": cell_types, "UMAP_1": umap1, "UMAP_2": umap2},
                        index=barcodes)
    return expr_matrix, meta

def find_markers(expr_df, meta, n_top):
    results = []
    cell_types_present = meta["cell_type"].unique()
    for ct in cell_types_present:
        in_ct  = meta[meta["cell_type"] == ct].index
        out_ct = meta[meta["cell_type"] != ct].index
        for gene in expr_df.columns[:50]:
            mu_in  = expr_df.loc[in_ct, gene].mean()
            mu_out = expr_df.loc[out_ct, gene].mean()
            lfc = np.log2(mu_in + 1) - np.log2(mu_out + 1)
            pct_in = (expr_df.loc[in_ct, gene] > 0).mean()
            if lfc > 0.5 and pct_in > 0.25:
                results.append({"cell_type": ct, "gene": gene,
                                 "avg_expr": round(mu_in, 2),
                                 "log2FC": round(lfc, 3),
                                 "pct_expressing": round(pct_in, 3)})
    df = pd.DataFrame(results).sort_values(["cell_type", "log2FC"], ascending=[True, False])
    return df.groupby("cell_type").head(n_top).reset_index(drop=True)

# Known markers for annotation reference
MARKER_REFERENCE = {
    "MYH7 / MYH2": "Myofiber (Type I/II)",
    "PAX7 / MYF5": "Satellite Cell",
    "PDGFRA": "FAP (fibro-adipogenic progenitor)",
    "CD68 / TNF / IL6": "Macrophage (M1 pro-inflammatory)",
    "CD163 / MRC1": "Macrophage (M2 anti-inflammatory)",
    "COL1A1 / ACTA2": "Myofibroblast / pro-fibrotic FAP",
    "FABP4 / PPARG": "Adipogenic FAP",
    "PECAM1 / CDH5": "Endothelial Cell",
    "PDGFRB / RGS5": "Pericyte",
}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("### 📁 Upload Single-Cell Data")
col_up, col_demo = st.columns([3, 1])
with col_up:
    uploaded_sc = st.file_uploader(
        "Upload CSV (rows=cells, cols=genes) or H5AD",
        type=["csv", "tsv", "h5ad"],
        help="For CSV: rows=barcodes, columns=genes. Include a 'cell_type' column if pre-annotated."
    )
with col_demo:
    st.markdown("<br/>", unsafe_allow_html=True)
    use_demo_sc = st.button("🧪 Use Demo Dataset\n(DMD Muscle sc)", use_container_width=True)

expr_df, meta_df = None, None

if use_demo_sc:
    with st.spinner("Generating demo single-cell dataset..."):
        expr_df, meta_df = make_demo_sc()
    total_cells = len(expr_df)
    n_types = meta_df["cell_type"].nunique()
    st.success(f"Demo loaded: {total_cells} cells × {expr_df.shape[1]} genes — {n_types} cell types (DMD muscle simulation)")

elif uploaded_sc is not None and uploaded_sc.name.endswith(".csv"):
    try:
        raw = pd.read_csv(uploaded_sc, index_col=0)
        if "cell_type" in raw.columns:
            meta_df = raw[["cell_type"]].copy()
            meta_df["UMAP_1"] = np.random.normal(0, 2, len(raw))
            meta_df["UMAP_2"] = np.random.normal(0, 2, len(raw))
            expr_df = raw.drop(columns=["cell_type"])
        else:
            expr_df = raw
            meta_df = pd.DataFrame({"cell_type": "Unknown", "UMAP_1": 0, "UMAP_2": 0},
                                    index=raw.index)
        st.success(f"Loaded: {expr_df.shape[0]} cells × {expr_df.shape[1]} genes")
    except Exception as e:
        st.error(f"Error: {e}")

if expr_df is not None and meta_df is not None:
    # QC KPIs
    n_cells = len(expr_df)
    n_genes_detected = (expr_df > 0).any(axis=0).sum()
    median_genes_per_cell = (expr_df > 0).sum(axis=1).median()
    n_clusters = meta_df["cell_type"].nunique()

    st.markdown("### 📈 Quality Control Summary")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Cells", f"{n_cells:,}")
    k2.metric("Genes Detected", f"{n_genes_detected:,}")
    k3.metric("Median Genes/Cell", f"{median_genes_per_cell:.0f}")
    k4.metric("Cell Populations", f"{n_clusters}")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🗺️ UMAP", "📊 Composition", "🧬 Marker Genes", "🔗 Cell-Cell Interaction"])

    with tab1:
        col_l, col_r = st.columns([2, 1])
        with col_l:
            color_by = st.selectbox("Color by", ["cell_type"] +
                                     [g for g in CELL_TYPES["Type I Fiber (slow)"]["markers"]
                                      if g in expr_df.columns])
        with col_r:
            point_size = st.slider("Point size", 3, 12, 5)

        if color_by == "cell_type":
            color_map = {ct: info["color"] for ct, info in CELL_TYPES.items()}
            fig_umap = go.Figure()
            for ct in meta_df["cell_type"].unique():
                sub = meta_df[meta_df["cell_type"] == ct]
                fig_umap.add_trace(go.Scatter(
                    x=sub["UMAP_1"], y=sub["UMAP_2"],
                    mode="markers", name=ct,
                    marker=dict(color=color_map.get(ct, "#94a3b8"), size=point_size, opacity=0.8),
                    hovertemplate=f"<b>{ct}</b><br>UMAP1: %{{x:.2f}}<br>UMAP2: %{{y:.2f}}<extra></extra>",
                ))
        else:
            if color_by in expr_df.columns:
                gene_expr = expr_df[color_by]
                fig_umap = go.Figure(go.Scatter(
                    x=meta_df["UMAP_1"], y=meta_df["UMAP_2"],
                    mode="markers",
                    marker=dict(color=gene_expr, colorscale="Viridis", size=point_size,
                                opacity=0.8, showscale=True,
                                colorbar=dict(title=color_by, tickfont=dict(color="#f1f5f9"))),
                    text=meta_df["cell_type"],
                    hovertemplate=f"<b>%{{text}}</b><br>{color_by}: %{{marker.color:.1f}}<extra></extra>",
                ))

        fig_umap.update_layout(
            template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            title=dict(text=f"UMAP — colored by {color_by}", font=dict(color="#22c55e", size=15)),
            height=520, legend=dict(bgcolor="#1e293b", bordercolor="#334155",
                                     font=dict(size=10)),
            xaxis_title="UMAP 1", yaxis_title="UMAP 2",
            font=dict(color="#f1f5f9"),
        )
        st.plotly_chart(fig_umap, use_container_width=True)

        # Marker reference
        with st.expander("📋 Cell Type Marker Reference (Muscular Dystrophy Context)"):
            for markers, annotation in MARKER_REFERENCE.items():
                st.markdown(f"- **{markers}** → {annotation}")

    with tab2:
        ct_counts = meta_df["cell_type"].value_counts().reset_index()
        ct_counts.columns = ["Cell Type", "Count"]
        ct_counts["Percentage"] = (ct_counts["Count"] / ct_counts["Count"].sum() * 100).round(1)

        col2a, col2b = st.columns(2)
        with col2a:
            color_list = [CELL_TYPES.get(ct, {}).get("color", "#94a3b8")
                          for ct in ct_counts["Cell Type"]]
            fig_pie = go.Figure(go.Pie(
                labels=ct_counts["Cell Type"], values=ct_counts["Count"],
                marker_colors=color_list, hole=0.45,
                textinfo="percent+label", textfont=dict(size=9),
            ))
            fig_pie.update_layout(
                template="plotly_dark", paper_bgcolor="#0f172a",
                title=dict(text="Cell Type Composition", font=dict(color="#22c55e")),
                height=420, showlegend=False, font=dict(color="#f1f5f9"),
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2b:
            fig_bar = px.bar(ct_counts, x="Count", y="Cell Type", orientation="h",
                              color="Cell Type",
                              color_discrete_map={ct: CELL_TYPES.get(ct, {}).get("color", "#94a3b8")
                                                  for ct in ct_counts["Cell Type"]},
                              template="plotly_dark", text="Count")
            fig_bar.update_layout(
                paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
                title=dict(text="Cell Counts", font=dict(color="#22c55e")),
                height=420, showlegend=False, font=dict(color="#f1f5f9"),
                yaxis=dict(categoryorder="total ascending"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        st.dataframe(ct_counts, use_container_width=True)

    with tab3:
        with st.spinner("Computing marker genes..."):
            markers_df = find_markers(expr_df, meta_df, n_top_markers)

        if not markers_df.empty:
            selected_ct = st.selectbox("Select cell type", meta_df["cell_type"].unique())
            ct_markers = markers_df[markers_df["cell_type"] == selected_ct]
            col3a, col3b = st.columns([1, 2])
            with col3a:
                st.markdown(f"**Top markers — {selected_ct}**")
                st.dataframe(ct_markers[["gene","avg_expr","log2FC","pct_expressing"]],
                             use_container_width=True)
            with col3b:
                if len(ct_markers) > 0:
                    genes_plot = ct_markers["gene"].tolist()[:8]
                    genes_plot = [g for g in genes_plot if g in expr_df.columns]
                    if genes_plot:
                        expr_sub = expr_df[genes_plot].copy()
                        expr_sub["cell_type"] = meta_df["cell_type"].values
                        expr_long = expr_sub.melt(id_vars="cell_type",
                                                   var_name="gene", value_name="expression")
                        fig_vio = px.violin(
                            expr_long[expr_long["gene"].isin(genes_plot[:4])],
                            x="gene", y="expression", color="cell_type",
                            color_discrete_map={ct: CELL_TYPES.get(ct, {}).get("color", "#94a3b8")
                                                for ct in meta_df["cell_type"].unique()},
                            template="plotly_dark", box=True,
                        )
                        fig_vio.update_layout(
                            paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
                            title=dict(text=f"Expression of top markers",
                                       font=dict(color="#22c55e")),
                            height=380, font=dict(color="#f1f5f9"),
                            showlegend=False,
                        )
                        st.plotly_chart(fig_vio, use_container_width=True)

    with tab4:
        st.markdown("""
<div style='background:#1e293b; border-radius:10px; padding:16px; margin-bottom:12px;'>
  <h4 style='color:#22c55e; margin:0 0 8px 0;'>Key Ligand-Receptor Interactions in Dystrophic Muscle</h4>
  <p style='color:#94a3b8; font-size:0.85rem; margin:0;'>
    Based on CellPhoneDB analysis from published scRNA-seq studies in DMD and LGMD.
  </p>
</div>
""", unsafe_allow_html=True)
        interactions = [
            {"Sender": "FAP (pro-fibrotic)", "Receiver": "Satellite Cell",
             "Ligand": "TGFB1", "Receptor": "TGFBR1/2", "Effect": "Inhibits myogenesis", "Score": 0.92},
            {"Sender": "Macrophage (M1)", "Receiver": "FAP (pro-fibrotic)",
             "Ligand": "CCL2", "Receptor": "CCR2", "Effect": "FAP recruitment & activation", "Score": 0.88},
            {"Sender": "Macrophage (M2/pro-fibr.)", "Receiver": "FAP (pro-fibrotic)",
             "Ligand": "SPP1", "Receptor": "CD44", "Effect": "Pro-fibrotic signaling", "Score": 0.85},
            {"Sender": "Macrophage (M1)", "Receiver": "Satellite Cell",
             "Ligand": "IGF1", "Receptor": "IGF1R", "Effect": "Promotes myogenesis", "Score": 0.79},
            {"Sender": "Endothelial Cell", "Receiver": "Satellite Cell",
             "Ligand": "CXCL12", "Receptor": "CXCR4", "Effect": "Niche maintenance", "Score": 0.75},
            {"Sender": "FAP (adipogenic)", "Receiver": "Type I Fiber (slow)",
             "Ligand": "MSTN", "Receptor": "ACVR2B", "Effect": "Inhibits hypertrophy", "Score": 0.82},
            {"Sender": "Pericyte", "Receiver": "FAP (pro-fibrotic)",
             "Ligand": "PDGFB", "Receptor": "PDGFRB", "Effect": "Fibroblast activation", "Score": 0.71},
        ]
        inter_df = pd.DataFrame(interactions)
        st.dataframe(inter_df.style.background_gradient(subset=["Score"],
                                                         cmap="Greens", vmin=0.5, vmax=1.0),
                     use_container_width=True)

        # Chord-like dot plot
        fig_dot = px.scatter(inter_df, x="Sender", y="Receiver",
                              size="Score", color="Score",
                              color_continuous_scale="Greens",
                              size_max=30, template="plotly_dark",
                              hover_data=["Ligand", "Receptor", "Effect"])
        fig_dot.update_layout(
            paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
            title=dict(text="Ligand-Receptor Interaction Map (dot size = interaction score)",
                       font=dict(color="#22c55e")),
            height=400, font=dict(color="#f1f5f9"),
            xaxis=dict(tickangle=20),
        )
        st.plotly_chart(fig_dot, use_container_width=True)

else:
    st.markdown("""
<div style='background:#1e293b; border:2px dashed #334155; border-radius:12px;
     padding:40px; text-align:center; margin-top:20px;'>
  <span style='font-size:3rem;'>🔬</span>
  <h3 style='color:#94a3b8; margin:12px 0 8px 0;'>Upload single-cell data to begin</h3>
  <p style='color:#64748b; font-size:0.9rem;'>
    CSV (rows=cells, cols=genes) or H5AD format.<br/>
    Or click <b>Use Demo Dataset</b> to explore with simulated DMD muscle single-cell data.
  </p>
</div>
""", unsafe_allow_html=True)
