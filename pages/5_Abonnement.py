import streamlit as st

st.set_page_config(page_title="MYOomics — Pricing", page_icon="💳", layout="wide")

st.markdown("""
<style>
.stApp {background-color:#0f172a; color:#f1f5f9;}
[data-testid="stSidebar"] {background-color:#0f172a;}
.stButton>button {background:linear-gradient(135deg,#1a4f8a,#3b82f6);color:white;border:none;border-radius:8px;font-weight:600;}
[data-testid="stExpander"] {background:#1e293b;border:1px solid #334155;border-radius:8px;}
input, textarea {background:#1e293b !important; color:#f1f5f9 !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='border-left:4px solid #3b82f6; padding-left:14px; margin-bottom:20px;'>
  <h2 style='color:#3b82f6; margin:0;'>💳 Pricing & Access</h2>
  <p style='color:#94a3b8; margin:4px 0 0 0; font-size:0.9rem;'>
    Choose the plan that fits your research or clinical needs —
    all plans include automated pipelines, PDF reports and dedicated support
  </p>
</div>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:20px 0 10px 0;'>
  <h3 style='color:#f1f5f9; font-size:1.6rem; margin:0 0 6px 0;'>
    Automate your multi-omics analysis pipeline
  </h3>
  <p style='color:#94a3b8; font-size:1rem; margin:0;'>
    From RNA-seq to single-cell to ML classification — standardized, reproducible,
    clinician-ready reports in minutes
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ── Pricing cards ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

plans = [
    {
        "name": "Academic",
        "icon": "🎓",
        "price": "2 000 – 5 000",
        "unit": "€ / year",
        "color": "#22c55e",
        "highlight": False,
        "features": [
            "✅ Bulk RNA-seq analysis",
            "✅ Volcano + heatmap",
            "✅ GO/KEGG enrichment",
            "✅ PDF reports",
            "✅ 5 analyses / month",
            "✅ GitHub open-source access",
            "❌ Single-cell module",
            "❌ ML classification",
            "❌ API access",
            "📧 Email support (48h)",
        ],
        "cta": "Request Academic Quote",
    },
    {
        "name": "Hospital / CHU",
        "icon": "🏥",
        "price": "8 000 – 15 000",
        "unit": "€ / year",
        "color": "#3b82f6",
        "highlight": False,
        "features": [
            "✅ Full RNA-seq pipeline",
            "✅ Single-cell / snRNA-seq",
            "✅ ML classification (RF/XGB/SVM)",
            "✅ SHAP explainability",
            "✅ PDF clinical reports",
            "✅ Unlimited analyses",
            "✅ GDPR-compliant data handling",
            "✅ On-premise deployment option",
            "❌ API access",
            "📞 Priority support (24h)",
        ],
        "cta": "Request Hospital Quote",
    },
    {
        "name": "Biotech / Pharma",
        "icon": "🔬",
        "price": "25 000 – 60 000",
        "unit": "€ / year",
        "color": "#a855f7",
        "highlight": True,
        "features": [
            "✅ Full omics pipeline",
            "✅ scRNA-seq + snRNA-seq",
            "✅ Epigenomics (ChIP/ATAC)",
            "✅ Proteomics integration",
            "✅ Multi-omics integration (MOFA)",
            "✅ REST API access",
            "✅ White-label option",
            "✅ Custom ML models",
            "✅ Unlimited analyses + storage",
            "🚀 Dedicated SLA + onboarding",
        ],
        "cta": "Request Enterprise Quote",
    },
    {
        "name": "Consulting",
        "icon": "💼",
        "price": "800 – 1 500",
        "unit": "€ / day",
        "color": "#f97316",
        "highlight": False,
        "features": [
            "✅ Custom analysis on your data",
            "✅ Pipeline development",
            "✅ Snakemake / Nextflow workflows",
            "✅ Statistical consulting",
            "✅ Manuscript preparation support",
            "✅ Team training (bioinformatics)",
            "✅ Grant application support",
            "✅ On-site or remote",
            "📅 Minimum 1 day engagement",
            "📋 Deliverable-based pricing",
        ],
        "cta": "Request Consulting",
    },
]

for col, plan in zip([col1, col2, col3, col4], plans):
    with col:
        border = f"2px solid {plan['color']}" if plan["highlight"] else f"1px solid {plan['color']}44"
        badge = f"<div style='background:{plan['color']}; color:white; font-size:0.7rem; font-weight:700; padding:3px 10px; border-radius:20px; margin-bottom:8px; display:inline-block;'>MOST POPULAR</div>" if plan["highlight"] else ""
        features_html = "".join(
            f"<div style='font-size:0.78rem; color:#cbd5e1; padding:2px 0;'>{f}</div>"
            for f in plan["features"]
        )
        st.markdown(f"""
<div style='background:#1e293b; border:{border}; border-radius:14px;
     padding:20px 16px; text-align:center; height:520px; position:relative;'>
  {badge}
  <div style='font-size:2rem;'>{plan["icon"]}</div>
  <h3 style='color:{plan["color"]}; margin:8px 0 4px 0; font-size:1.05rem;'>{plan["name"]}</h3>
  <div style='color:#f1f5f9; font-size:1.4rem; font-weight:700; margin:6px 0 2px 0;'>
    {plan["price"]}
  </div>
  <div style='color:#94a3b8; font-size:0.8rem; margin-bottom:12px;'>{plan["unit"]}</div>
  <hr style='border-color:#334155; margin:8px 0;'/>
  <div style='text-align:left;'>{features_html}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ── Feature comparison table ───────────────────────────────────────────────────
with st.expander("📊 Full Feature Comparison Table"):
    features = [
        ("Bulk RNA-seq (DESeq2 pipeline)", "✅", "✅", "✅", "✅"),
        ("Volcano plot + heatmap", "✅", "✅", "✅", "✅"),
        ("GO / KEGG enrichment", "✅", "✅", "✅", "✅"),
        ("PDF report generation", "✅", "✅", "✅", "✅"),
        ("Single-cell RNA-seq (Scanpy/Seurat)", "❌", "✅", "✅", "✅"),
        ("snRNA-seq analysis", "❌", "✅", "✅", "✅"),
        ("ML classification (RF/XGB/SVM)", "❌", "✅", "✅", "✅"),
        ("SHAP explainability", "❌", "✅", "✅", "✅"),
        ("Epigenomics (ChIP/ATAC-seq)", "❌", "❌", "✅", "✅"),
        ("Proteomics integration", "❌", "❌", "✅", "✅"),
        ("Multi-omics integration (MOFA)", "❌", "❌", "✅", "✅"),
        ("REST API access", "❌", "❌", "✅", "✅"),
        ("White-label / on-premise", "❌", "✅", "✅", "✅"),
        ("GDPR compliance certification", "❌", "✅", "✅", "✅"),
        ("Monthly analyses", "5", "Unlimited", "Unlimited", "Per project"),
        ("Support response time", "48h email", "24h priority", "Dedicated SLA", "Per contract"),
    ]
    import pandas as pd
    df_feat = pd.DataFrame(features,
        columns=["Feature", "Academic", "Hospital/CHU", "Biotech/Pharma", "Consulting"])
    st.dataframe(df_feat, use_container_width=True, hide_index=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ── Contact form ──────────────────────────────────────────────────────────────
st.markdown("### 📬 Request a Quote or Demo")
col_form, col_info = st.columns([2, 1])

with col_form:
    with st.form("contact_form"):
        c1, c2 = st.columns(2)
        with c1:
            contact_name = st.text_input("Full name *")
            contact_email = st.text_input("Email *")
            contact_org = st.text_input("Institution / Company *")
        with c2:
            contact_plan = st.selectbox("Plan of interest *",
                ["Academic", "Hospital / CHU", "Biotech / Pharma", "Consulting", "Custom"])
            contact_country = st.text_input("Country")
            contact_data = st.selectbox("Data type",
                ["Bulk RNA-seq", "scRNA-seq / snRNA-seq", "ChIP-seq / ATAC-seq",
                 "Proteomics", "Multi-omics", "Other"])
        contact_msg = st.text_area("Message / specific needs", height=100,
            placeholder="Describe your project, sample numbers, timeline...")
        submitted = st.form_submit_button("🚀 Send Request", use_container_width=True)
        if submitted:
            if contact_name and contact_email and contact_org:
                st.success(f"""
Request received! We'll contact you at **{contact_email}** within 24–48 hours.

**Summary:** {contact_name} — {contact_org} — {contact_plan} plan — {contact_data}
""")
            else:
                st.error("Please fill in all required fields (*).")

with col_info:
    st.markdown("""
<div style='background:#1e293b; border-radius:12px; padding:20px;
     border-left:4px solid #3b82f6;'>
  <h4 style='color:#3b82f6; margin:0 0 12px 0;'>Why MYOomics?</h4>

  <div style='margin-bottom:10px;'>
    <b style='color:#f1f5f9;'>🧬 Science-backed</b>
    <p style='color:#94a3b8; font-size:0.82rem; margin:3px 0 0 0;'>
      Built on a PRISMA 2020 systematic review of 67 multi-omics studies,
      4,213 samples (TALL ML, medRxiv 2026)
    </p>
  </div>

  <div style='margin-bottom:10px;'>
    <b style='color:#f1f5f9;'>⚡ Automated pipelines</b>
    <p style='color:#94a3b8; font-size:0.82rem; margin:3px 0 0 0;'>
      From raw counts to publication-ready figures in minutes —
      no bioinformatics expertise required
    </p>
  </div>

  <div style='margin-bottom:10px;'>
    <b style='color:#f1f5f9;'>🔒 GDPR compliant</b>
    <p style='color:#94a3b8; font-size:0.82rem; margin:3px 0 0 0;'>
      Patient data processed according to GDPR/CNIL regulations —
      on-premise deployment available
    </p>
  </div>

  <div style='margin-bottom:10px;'>
    <b style='color:#f1f5f9;'>🌍 AFM-Téléthon aligned</b>
    <p style='color:#94a3b8; font-size:0.82rem; margin:3px 0 0 0;'>
      Developed in partnership with MYOccitanie program —
      INSERM U1046 / CNRS UMR 9214, Montpellier
    </p>
  </div>

  <hr style='border-color:#334155; margin:12px 0;'/>

  <div style='font-size:0.82rem; color:#94a3b8;'>
    <b style='color:#f1f5f9;'>Contact direct:</b><br/>
    Dr. Mamadou Lamine TALL, PhD<br/>
    📧 laminetall30@gmail.com<br/>
    🔗 github.com/mamadoulaminetall/myoomics
  </div>
</div>
""", unsafe_allow_html=True)

# ── FAQ ────────────────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("### ❓ Frequently Asked Questions")

faqs = [
    ("What data formats does MYOomics accept?",
     "CSV/TSV count matrices for bulk RNA-seq, H5AD (AnnData) for single-cell data, "
     "and standard BED/BAM-derived files for epigenomics. File size up to 500 MB per upload."),
    ("Is patient data secure?",
     "Yes. MYOomics is GDPR and CNIL compliant. Data is processed transiently and not stored "
     "permanently on our servers. On-premise deployment (Docker/Singularity) is available "
     "for Hospital/CHU and Biotech/Pharma plans."),
    ("Do I need bioinformatics expertise to use the platform?",
     "No. MYOomics is designed for clinicians and biologists. Upload your data, select "
     "parameters, click Analyze. The platform handles alignment, normalization, "
     "differential analysis and report generation automatically."),
    ("Can MYOomics integrate with existing pipelines?",
     "Yes. The Biotech/Pharma plan includes REST API access compatible with Snakemake, "
     "Nextflow and Galaxy workflows. Custom integration is available via consulting."),
    ("Is MYOomics open-source?",
     "The core analysis modules are open-source (GitHub: mamadoulaminetall/myoomics, MIT license). "
     "The SaaS platform with automated pipelines, reports and support is a paid service."),
    ("How is pricing determined for the Consulting tier?",
     "Consulting is billed per day (800–1,500 EUR) based on project complexity. "
     "A free 30-minute scoping call is available to estimate the engagement."),
]

for q, a in faqs:
    with st.expander(f"❓ {q}"):
        st.markdown(f"<p style='color:#94a3b8; font-size:0.9rem;'>{a}</p>",
                    unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color:#475569; font-size:0.78rem; padding:10px 0;'>
  MYOomics v1.0.0 — Dr. Mamadou Lamine TALL, PhD — Aix-Marseille Universite<br/>
  For research use. Prices in EUR excluding taxes. Subscription conditions on request.<br/>
  🧬 github.com/mamadoulaminetall/myoomics
</div>
""", unsafe_allow_html=True)
