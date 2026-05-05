import streamlit as st

st.set_page_config(
    page_title="MYOomics — Multi-Omics Analysis Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Sidebar */
[data-testid="stSidebar"] {background-color: #0f172a;}
[data-testid="stSidebar"] * {color: #f1f5f9;}

/* Main background */
.stApp {background-color: #0f172a; color: #f1f5f9;}

/* Metric cards */
[data-testid="stMetric"] {
    background: #1e293b;
    border-radius: 10px;
    padding: 12px;
    border: 1px solid #334155;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #1a4f8a, #3b82f6);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #2c6eb5, #60a5fa);
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    background: #1e293b;
    border-radius: 8px 8px 0 0;
    color: #94a3b8;
}
.stTabs [aria-selected="true"] {
    background: #1a4f8a;
    color: white;
}

/* DataFrames */
[data-testid="stDataFrame"] {background: #1e293b; border-radius: 8px;}

/* Divider */
hr {border-color: #334155;}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #1e293b;
    border: 2px dashed #334155;
    border-radius: 10px;
}

/* Expander */
[data-testid="stExpander"] {background: #1e293b; border: 1px solid #334155; border-radius: 8px;}

/* Select boxes */
.stSelectbox > div > div {background: #1e293b; color: #f1f5f9;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style='text-align:center; padding: 16px 0 8px 0;'>
  <span style='font-size:2.2rem;'>🧬</span>
  <h2 style='color:#3b82f6; margin:4px 0 2px 0; font-size:1.5rem;'>MYOomics</h2>
  <p style='color:#94a3b8; font-size:0.78rem; margin:0;'>
    Multi-Omics Analysis Platform<br/>for Muscular Dystrophies
  </p>
</div>
<hr style='border-color:#334155; margin:10px 0;'/>
""", unsafe_allow_html=True)

    st.markdown("""
<div style='color:#64748b; font-size:0.75rem; padding: 8px 0;'>
  <b style='color:#94a3b8;'>NAVIGATION</b>
</div>
""", unsafe_allow_html=True)

    st.page_link("app.py",                          label="🏠  Home",                  )
    st.page_link("pages/1_RNAseq_Bulk.py",          label="📊  Bulk RNA-seq Analysis"  )
    st.page_link("pages/2_SingleCell.py",            label="🔬  Single-Cell / snRNA-seq")
    st.page_link("pages/3_ML_Classification.py",     label="🤖  ML Classification"      )
    st.page_link("pages/4_Rapport.py",               label="📄  Report Generator"        )
    st.page_link("pages/5_Abonnement.py",            label="💳  Pricing & Access"        )
    st.markdown("""<a href="https://buy.stripe.com/fZu8wP8VycBf20udzob3q08" target="_blank" style="display:block;background:linear-gradient(135deg,#10b981,#059669);color:white;text-align:center;padding:11px 16px;border-radius:9px;font-weight:700;text-decoration:none;font-size:0.87rem;margin-top:12px">💳 S'abonner — 149€/mois</a>""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#334155; margin:12px 0;'/>", unsafe_allow_html=True)
    st.markdown("""
<div style='font-size:0.72rem; color:#64748b; text-align:center;'>
  Dr. Mamadou Lamine TALL, PhD<br/>
  Aix-Marseille Universite<br/>
  <a href='https://github.com/mamadoulaminetall/myoomics'
     style='color:#3b82f6;'>github.com/mamadoulaminetall</a><br/><br/>
  v1.0.0 — April 2026
</div>
""", unsafe_allow_html=True)

# ── Home page ────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 20px 0 10px 0;'>
  <span style='font-size:3rem;'>🧬</span>
  <h1 style='color:#3b82f6; font-size:2.5rem; margin:8px 0 4px 0;'>MYOomics</h1>
  <p style='color:#94a3b8; font-size:1.1rem; margin:0;'>
    Automated Multi-Omics Analysis Platform for Inherited Muscular Dystrophies
  </p>
</div>
<hr style='border-color:#334155; margin:16px 0;'/>
""", unsafe_allow_html=True)

# Feature cards
col1, col2, col3, col4 = st.columns(4)
cards = [
    ("📊", "Bulk RNA-seq", "Differential expression analysis with volcano plots, heatmaps and GO/KEGG enrichment", "#1a4f8a"),
    ("🔬", "Single-Cell", "scRNA-seq & snRNA-seq: UMAP, clustering, marker genes, CellChat ligand-receptor", "#1e5a2e"),
    ("🤖", "ML Classification", "Random Forest, XGBoost, SVM with SHAP explainability for patient stratification", "#5a1a6e"),
    ("📄", "Auto Reports", "One-click PDF report generation with full statistical summary and visualizations", "#6e3a1a"),
]
for col, (icon, title, desc, color) in zip([col1, col2, col3, col4], cards):
    with col:
        st.markdown(f"""
<div style='background:{color}22; border:1px solid {color}66;
     border-radius:12px; padding:18px; text-align:center; height:180px;'>
  <div style='font-size:2rem;'>{icon}</div>
  <h3 style='color:#f1f5f9; font-size:1rem; margin:8px 0 6px 0;'>{title}</h3>
  <p style='color:#94a3b8; font-size:0.8rem; margin:0; line-height:1.4;'>{desc}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Scientific context
col_left, col_right = st.columns([3, 2])
with col_left:
    st.markdown("""
<div style='background:#1e293b; border-radius:12px; padding:20px;
     border-left:4px solid #3b82f6;'>
  <h3 style='color:#3b82f6; margin:0 0 10px 0;'>Scientific Framework</h3>
  <p style='color:#cbd5e1; font-size:0.92rem; line-height:1.6; margin:0;'>
    MYOomics is grounded in a PRISMA 2020 systematic review of <b style='color:#f1f5f9;'>67
    multi-omics studies</b> encompassing <b style='color:#f1f5f9;'>4,213 samples</b> from
    12 inherited muscular dystrophy subtypes (2000-2026).<br/><br/>
    Three convergent molecular axes identified across omics layers guide the platform analytics:
    <br/>• DAGC disassembly / NF-kB inflammation (RNA-seq + proteomics)
    <br/>• Epigenetic reprogramming toward fibrosis (ChIP-seq + ATAC-seq)
    <br/>• Satellite cell exhaustion (scRNA-seq + H3K27me3)
    <br/><br/>
    <b style='color:#f1f5f9;'>Priority therapeutic targets:</b>
    UTRN, MSTN, FOXO3, NRF2 (convergent across ≥3 omics layers)
  </p>
</div>
""", unsafe_allow_html=True)

with col_right:
    st.markdown("""
<div style='background:#1e293b; border-radius:12px; padding:20px;
     border-left:4px solid #10b981;'>
  <h3 style='color:#10b981; margin:0 0 12px 0;'>Platform Capabilities</h3>
""", unsafe_allow_html=True)
    caps = [
        ("📥", "Upload", "CSV, TSV, H5AD up to 500 MB"),
        ("⚡", "Analysis", "PyDESeq2, Scanpy, scikit-learn"),
        ("🎯", "ML", "RF, XGBoost, SVM + SHAP"),
        ("🗺️", "Single-cell", "UMAP, Leiden clustering, markers"),
        ("📊", "Enrichment", "GO, KEGG, GSEA pathway analysis"),
        ("📄", "Export", "PDF reports, CSV downloads"),
    ]
    for icon, name, desc in caps:
        st.markdown(f"""
<div style='display:flex; align-items:center; margin-bottom:8px;'>
  <span style='font-size:1.1rem; margin-right:8px;'>{icon}</span>
  <div>
    <span style='color:#f1f5f9; font-size:0.88rem; font-weight:600;'>{name}</span>
    <span style='color:#94a3b8; font-size:0.82rem;'> — {desc}</span>
  </div>
</div>
""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Diseases covered
st.markdown("""
<div style='background:#1e293b; border-radius:12px; padding:16px;'>
  <h3 style='color:#f1f5f9; margin:0 0 12px 0; font-size:1rem;'>
    Diseases Covered — Inherited Muscular Dystrophies
  </h3>
""", unsafe_allow_html=True)
diseases = [
    ("DMD", "Duchenne Muscular Dystrophy", "#ef4444"),
    ("BMD", "Becker Muscular Dystrophy", "#f97316"),
    ("LGMD", "Limb-Girdle MD (>30 subtypes)", "#eab308"),
    ("DM1/2", "Myotonic Dystrophy", "#22c55e"),
    ("FSHD", "Facioscapulohumeral MD", "#3b82f6"),
    ("EDMD", "Emery-Dreifuss MD", "#a855f7"),
]
cols = st.columns(6)
for col, (abbr, full, color) in zip(cols, diseases):
    with col:
        st.markdown(f"""
<div style='background:{color}22; border:1px solid {color}66;
     border-radius:8px; padding:10px; text-align:center;'>
  <b style='color:{color}; font-size:0.9rem;'>{abbr}</b>
  <p style='color:#94a3b8; font-size:0.7rem; margin:4px 0 0 0; line-height:1.3;'>{full}</p>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color:#475569; font-size:0.78rem;'>
  MYOomics v1.0.0 — Dr. Mamadou Lamine TALL, PhD — Aix-Marseille Universite — April 2026<br/>
  Associated systematic review: <i>Multi-Omics Profiling in Inherited Muscular Dystrophies</i>
  (TALL ML, 2026) — medRxiv preprint
</div>
""", unsafe_allow_html=True)
