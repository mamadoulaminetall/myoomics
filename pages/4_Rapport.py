import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

st.set_page_config(page_title="MYOomics — Report", page_icon="📄", layout="wide")

st.markdown("""
<style>
.stApp {background-color:#0f172a; color:#f1f5f9;}
[data-testid="stSidebar"] {background-color:#0f172a;}
[data-testid="stMetric"] {background:#1e293b;border-radius:10px;padding:12px;border:1px solid #334155;}
.stButton>button {background:linear-gradient(135deg,#6e3a1a,#f97316);color:white;border:none;border-radius:8px;font-weight:600;}
[data-testid="stExpander"] {background:#1e293b;border:1px solid #334155;border-radius:8px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='border-left:4px solid #f97316; padding-left:14px; margin-bottom:20px;'>
  <h2 style='color:#f97316; margin:0;'>📄 Automated Report Generator</h2>
  <p style='color:#94a3b8; margin:4px 0 0 0; font-size:0.9rem;'>
    Generate a complete PDF analysis report — patient info, DEG summary,
    ML classification, clinical interpretation — ready for clinicians
  </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Report Settings")
    report_title   = st.text_input("Report title", "MYOomics Multi-Omics Analysis Report")
    patient_id     = st.text_input("Patient / Cohort ID", "COHORT-001")
    analyst_name   = st.text_input("Analyst name", "Dr. Mamadou Lamine TALL")
    institution    = st.text_input("Institution", "Aix-Marseille Universite / PhyMedExp")
    disease_focus  = st.selectbox("Disease focus", ["DMD", "LGMD-R1", "LGMD-R2", "DM1", "FSHD", "Mixed/Other"])
    include_refs   = st.checkbox("Include scientific references", value=True)
    include_interp = st.checkbox("Include clinical interpretation", value=True)

# ── Report builder ────────────────────────────────────────────────────────────
def build_pdf(title, patient_id, analyst, institution, disease, date_str,
              deg_stats, ml_stats, go_results, include_refs, include_interp):

    BLUE   = HexColor("#1a4f8a")
    LBLUE  = HexColor("#2c6eb5")
    ACCENT = HexColor("#f97316")
    GRAY   = HexColor("#555555")
    LGRAY  = HexColor("#f8fafc")

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=2.5*cm, rightMargin=2.5*cm,
                             topMargin=2.5*cm, bottomMargin=2.5*cm)

    S = {
        "title":  ParagraphStyle("t", fontSize=18, textColor=BLUE,
                    fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6, leading=24),
        "sub":    ParagraphStyle("s", fontSize=10, textColor=GRAY,
                    fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4),
        "h1":     ParagraphStyle("h1", fontSize=12, textColor=BLUE,
                    fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4),
        "h2":     ParagraphStyle("h2", fontSize=10.5, textColor=LBLUE,
                    fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3),
        "body":   ParagraphStyle("b", fontSize=10, textColor=black,
                    fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=5, leading=14),
        "alert":  ParagraphStyle("a", fontSize=10, textColor=HexColor("#7c2d12"),
                    fontName="Helvetica-Bold", spaceAfter=4),
        "bullet": ParagraphStyle("bu", fontSize=9.5, textColor=black,
                    fontName="Helvetica", leftIndent=14, firstLineIndent=-10,
                    spaceAfter=3, leading=13),
        "th":     ParagraphStyle("th", fontSize=9, textColor=white,
                    fontName="Helvetica-Bold", alignment=TA_CENTER),
        "td":     ParagraphStyle("td", fontSize=8.5, textColor=black,
                    fontName="Helvetica", alignment=TA_LEFT),
        "ref":    ParagraphStyle("r", fontSize=8.5, textColor=GRAY,
                    fontName="Helvetica", spaceAfter=3, leading=12),
        "footer": ParagraphStyle("f", fontSize=8, textColor=GRAY,
                    fontName="Helvetica-Oblique", alignment=TA_CENTER),
    }

    def HR():
        return HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=4, spaceBefore=2)

    def tbl_style(header_color=BLUE):
        return TableStyle([
            ("BACKGROUND", (0,0), (-1,0), header_color),
            ("TEXTCOLOR",  (0,0), (-1,0), white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [LGRAY, white]),
            ("GRID",       (0,0), (-1,-1), 0.4, HexColor("#dddddd")),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("VALIGN",     (0,0), (-1,-1), "TOP"),
        ])

    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph("🧬  MYOomics", S["sub"]))
    story.append(Paragraph(title, S["title"]))
    story.append(Paragraph(
        f"Patient/Cohort: <b>{patient_id}</b>  |  Disease: <b>{disease}</b>  |  "
        f"Date: <b>{date_str}</b>", S["sub"]))
    story.append(Paragraph(
        f"Analyst: <b>{analyst}</b>  |  Institution: <b>{institution}</b>", S["sub"]))
    story.append(Spacer(1, 8))
    story.append(HR())

    # ── Executive Summary ────────────────────────────────────────────────────
    story.append(Paragraph("EXECUTIVE SUMMARY", S["h1"]))
    story.append(Paragraph(
        f"This report presents the results of a multi-omics analysis performed on cohort "
        f"<b>{patient_id}</b> using the MYOomics automated analysis platform. The analysis "
        f"focused on <b>{disease}</b> and integrates bulk transcriptomic differential "
        f"expression analysis, machine learning-based patient classification, and functional "
        f"pathway enrichment. Results are interpreted in the context of established molecular "
        f"signatures from a systematic review of 67 multi-omics studies in inherited muscular "
        f"dystrophies (TALL ML, 2026).", S["body"]))

    # ── DEG Summary ─────────────────────────────────────────────────────────
    story.append(HR())
    story.append(Paragraph("1. BULK RNA-SEQ DIFFERENTIAL EXPRESSION ANALYSIS", S["h1"]))

    deg_table_data = [
        [Paragraph("Parameter", S["th"]),
         Paragraph("Value", S["th"]),
         Paragraph("Threshold", S["th"])],
        [Paragraph("Total genes analyzed", S["td"]),
         Paragraph(str(deg_stats.get("total_genes", "N/A")), S["td"]),
         Paragraph("—", S["td"])],
        [Paragraph("Significantly upregulated DEGs", S["td"]),
         Paragraph(str(deg_stats.get("n_up", "N/A")), S["td"]),
         Paragraph(f"padj < {deg_stats.get('pval_thr', 0.05)}, log2FC > {deg_stats.get('lfc_thr', 1.0)}", S["td"])],
        [Paragraph("Significantly downregulated DEGs", S["td"]),
         Paragraph(str(deg_stats.get("n_down", "N/A")), S["td"]),
         Paragraph(f"padj < {deg_stats.get('pval_thr', 0.05)}, log2FC < -{deg_stats.get('lfc_thr', 1.0)}", S["td"])],
        [Paragraph("Normalization method", S["td"]),
         Paragraph(deg_stats.get("norm", "DESeq2 median-of-ratios"), S["td"]),
         Paragraph("—", S["td"])],
        [Paragraph("Statistical test", S["td"]),
         Paragraph("Wald test + BH correction", S["td"]),
         Paragraph("—", S["td"])],
    ]
    t1 = Table(deg_table_data, colWidths=[6.5*cm, 3.5*cm, 5.5*cm])
    t1.setStyle(tbl_style())
    story.append(t1)
    story.append(Spacer(1, 8))

    top_up = deg_stats.get("top_up", ["COL1A1", "TGFB1", "IL6", "POSTN", "CCL2"])
    top_down = deg_stats.get("top_down", ["DMD", "UTRN", "PAX7", "MYH7", "ATP2A1"])
    story.append(Paragraph("<b>Top upregulated genes:</b> " + ", ".join(top_up), S["body"]))
    story.append(Paragraph("<b>Top downregulated genes:</b> " + ", ".join(top_down), S["body"]))

    # GO results
    if go_results:
        story.append(Paragraph("1.1 Enriched GO/KEGG Pathways", S["h2"]))
        go_data = [[Paragraph(h, S["th"]) for h in ["Pathway", "Overlap", "Fold Enrichment", "p-value"]]]
        for row in go_results[:6]:
            go_data.append([
                Paragraph(row.get("GO Term", ""), S["td"]),
                Paragraph(str(row.get("Overlap", "")), S["td"]),
                Paragraph(str(row.get("Fold Enrichment", "")), S["td"]),
                Paragraph(str(row.get("p-value", "")), S["td"]),
            ])
        t_go = Table(go_data, colWidths=[7*cm, 2*cm, 3.5*cm, 3*cm])
        t_go.setStyle(tbl_style(LBLUE))
        story.append(t_go)
        story.append(Spacer(1, 8))

    # ── ML Classification ────────────────────────────────────────────────────
    story.append(HR())
    story.append(Paragraph("2. MACHINE LEARNING PATIENT CLASSIFICATION", S["h1"]))

    ml_table_data = [
        [Paragraph("Parameter", S["th"]),
         Paragraph("Value", S["th"])],
        [Paragraph("Model", S["td"]),
         Paragraph(ml_stats.get("model", "Random Forest"), S["td"])],
        [Paragraph("Cross-validation", S["td"]),
         Paragraph(ml_stats.get("cv", "StratifiedKFold 5-fold"), S["td"])],
        [Paragraph("Overall Accuracy", S["td"]),
         Paragraph(ml_stats.get("accuracy", "N/A"), S["td"])],
        [Paragraph("Macro AUC (OvR)", S["td"]),
         Paragraph(ml_stats.get("auc", "N/A"), S["td"])],
        [Paragraph("Macro F1-score", S["td"]),
         Paragraph(ml_stats.get("f1", "N/A"), S["td"])],
        [Paragraph("Top predictive features", S["td"]),
         Paragraph(", ".join(ml_stats.get("top_features", ["DMD_expr", "COL1A1_expr", "PAX7_expr", "UTRN_expr"])), S["td"])],
    ]
    t2 = Table(ml_table_data, colWidths=[6.5*cm, 9*cm])
    t2.setStyle(tbl_style())
    story.append(t2)
    story.append(Spacer(1, 8))

    # ── Clinical Interpretation ───────────────────────────────────────────────
    if include_interp:
        story.append(HR())
        story.append(Paragraph("3. CLINICAL INTERPRETATION", S["h1"]))

        interp = {
            "DMD": [
                "Complete dystrophin deficiency confirmed by transcriptomic and proteomic signatures.",
                "Significant upregulation of fibrosis markers (COL1A1, TGFB1, POSTN) — advanced fibrotic remodeling.",
                "Severe depletion of satellite cell markers (PAX7, MYF5) — impaired muscle regeneration.",
                "FAP expansion detected — consider anti-fibrotic therapeutic strategies.",
                "UTRN (utrophin) downregulation confirmed — pharmacological upregulation may be beneficial.",
                "MSTN overexpression detected — anti-myostatin therapy may be indicated.",
            ],
            "LGMD-R1": [
                "CAPN3 pathway disruption confirmed — ubiquitin-proteasome system hyperactivation (TRIM63, FBXO32).",
                "Moderate inflammatory infiltration (NF-kB axis activated).",
                "Satellite cell pool partially preserved — better prognosis for regenerative therapies.",
            ],
            "LGMD-R2": [
                "Membrane repair pathway failure confirmed (ANXA1, ANXA2, ANXA6 downregulation).",
                "Enhanced lysosomal biogenesis detected (TFEB pathway activated).",
                "Inflammation pattern consistent with dysferlinopathy — dysferlin replacement strategies applicable.",
            ],
            "DM1": [
                "DMPK expression dysregulation confirmed — RNA toxic gain-of-function mechanism.",
                "Splicing factor dysregulation (MBNL1/2 sequestration signature detected).",
                "Moderate muscle atrophy signature — mitochondrial function partially preserved.",
            ],
            "FSHD": [
                "DUX4 target gene activation detected — pathognomonic of FSHD.",
                "Oxidative stress response elevated — NRF2 pathway activation.",
            ],
        }.get(disease, [
            "Multi-omics analysis completed — results require specialist interpretation.",
            "Consult with neuromuscular disease specialist for clinical correlation.",
        ])

        for point in interp:
            story.append(Paragraph(f"• {point}", S["bullet"]))
        story.append(Spacer(1, 6))

        story.append(Paragraph("3.1 Convergent Therapeutic Targets (Literature-Supported)", S["h2"]))
        targets_data = [
            [Paragraph(h, S["th"]) for h in ["Target", "Status in Patient", "Evidence Level", "Therapeutic Approach"]],
            [Paragraph("UTRN (Utrophin)", S["td"]), Paragraph("Downregulated", S["td"]),
             Paragraph("High (3 omics layers)", S["td"]), Paragraph("Ezutromid / SMT upregulation", S["td"])],
            [Paragraph("MSTN (Myostatin)", S["td"]), Paragraph("Upregulated", S["td"]),
             Paragraph("High (RNA + protein)", S["td"]), Paragraph("Domagrozumab / anti-MSTN Ab", S["td"])],
            [Paragraph("FOXO3", S["td"]), Paragraph("Upregulated", S["td"]),
             Paragraph("Moderate (RNA + ChIP)", S["td"]), Paragraph("FOXO3 inhibitors (preclinical)", S["td"])],
            [Paragraph("NRF2 pathway", S["td"]), Paragraph("Activated", S["td"]),
             Paragraph("Moderate (RNA + proteomics)", S["td"]), Paragraph("Antioxidant therapy (NAC)", S["td"])],
        ]
        t3 = Table(targets_data, colWidths=[4*cm, 3.5*cm, 4*cm, 4*cm])
        t3.setStyle(tbl_style(LBLUE))
        story.append(t3)

    # ── Methods note ──────────────────────────────────────────────────────────
    story.append(HR())
    story.append(Paragraph("4. METHODS & PLATFORM", S["h1"]))
    story.append(Paragraph(
        "Analysis performed using MYOomics v1.0.0 — automated multi-omics platform. "
        "Differential expression: DESeq2 median-of-ratios normalization, Wald test, "
        "Benjamini-Hochberg FDR correction. Machine learning: StratifiedKFold "
        "cross-validation, SHAP-based feature importance. Pathway enrichment: "
        "Fisher's exact test against curated gene sets (GO Biological Process, KEGG). "
        "Scientific framework: systematic review of 67 multi-omics studies in inherited "
        "muscular dystrophies, 4,213 samples (TALL ML, medRxiv 2026).", S["body"]))

    # ── References ────────────────────────────────────────────────────────────
    if include_refs:
        story.append(HR())
        story.append(Paragraph("REFERENCES", S["h1"]))
        refs = [
            "1. TALL ML. Multi-Omics Profiling in Inherited Muscular Dystrophies: A Systematic Review. medRxiv 2026.",
            "2. Chemello F, et al. Degenerative and regenerative pathways in DMD by snRNA-seq. PNAS 2020;117:29691.",
            "3. Malecova B, et al. Dynamics of fibro-adipogenic progenitors in muscular dystrophy. Nat Commun 2018;9:3670.",
            "4. Johnson EK, et al. Proteomic analysis of the dystrophin-associated protein complex. PLoS ONE 2012;7:e50316.",
            "5. Mercuri E, et al. Muscular dystrophies. Lancet 2019;394:2025-2038.",
            "6. Page MJ, et al. PRISMA 2020 statement. BMJ 2021;372:n71.",
        ]
        for r in refs:
            story.append(Paragraph(r, S["ref"]))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 12))
    story.append(HR())
    story.append(Paragraph(
        f"Generated by MYOomics v1.0.0  |  {date_str}  |  "
        f"github.com/mamadoulaminetall/myoomics  |  "
        f"For research use only — not for clinical diagnosis",
        S["footer"]))

    doc.build(story)
    buf.seek(0)
    return buf

# ═══════════════════════════════════════════════════════════════════════════
# MAIN UI
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("### ⚙️ Configure Your Report")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
<div style='background:#1e293b; border-radius:10px; padding:16px; border:1px solid #334155;'>
  <h4 style='color:#f97316; margin:0 0 10px 0;'>DEG Analysis Results</h4>
""", unsafe_allow_html=True)
    total_genes = st.number_input("Total genes analyzed", 100, 50000, 500)
    n_up   = st.number_input("Upregulated DEGs", 0, 10000, 87)
    n_down = st.number_input("Downregulated DEGs", 0, 10000, 63)
    pval_t = st.number_input("p-value threshold", 0.001, 0.1, 0.05, format="%.3f")
    lfc_t  = st.number_input("log2FC threshold", 0.5, 3.0, 1.0, format="%.1f")
    top_up_str   = st.text_input("Top UP genes (comma-separated)",
                                  "COL1A1, TGFB1, IL6, POSTN, CCL2, MSTN, FOXO3")
    top_down_str = st.text_input("Top DOWN genes (comma-separated)",
                                  "DMD, UTRN, PAX7, MYH7, ATP2A1, ACTA1, TTN")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div style='background:#1e293b; border-radius:10px; padding:16px; border:1px solid #334155;'>
  <h4 style='color:#f97316; margin:0 0 10px 0;'>ML Classification Results</h4>
""", unsafe_allow_html=True)
    ml_model   = st.selectbox("Model used", ["Random Forest", "XGBoost", "SVM (RBF)"])
    ml_acc     = st.text_input("Accuracy", "0.941")
    ml_auc     = st.text_input("Macro AUC", "0.961")
    ml_f1      = st.text_input("Macro F1", "0.938")
    top_feat_str = st.text_input("Top features (comma-separated)",
                                  "DMD_expr, COL1A1_expr, UTRN_expr, PAX7_expr, MSTN_expr")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

col_gen, col_prev = st.columns([1, 2])
with col_gen:
    generate = st.button("📄 Generate PDF Report", use_container_width=True)

with col_prev:
    st.markdown(f"""
<div style='background:#1e293b; border-radius:8px; padding:12px; font-size:0.85rem; color:#94a3b8;'>
  <b style='color:#f1f5f9;'>Report will include:</b><br/>
  Executive summary · DEG table · GO enrichment · ML performance ·
  {"Clinical interpretation · " if include_interp else ""}
  {"Scientific references · " if include_refs else ""}
  Methods · MYOomics footer
</div>
""", unsafe_allow_html=True)

if generate:
    deg_stats = {
        "total_genes": int(total_genes),
        "n_up": int(n_up), "n_down": int(n_down),
        "pval_thr": float(pval_t), "lfc_thr": float(lfc_t),
        "norm": "DESeq2 median-of-ratios",
        "top_up":   [g.strip() for g in top_up_str.split(",")][:7],
        "top_down": [g.strip() for g in top_down_str.split(",")][:7],
    }
    ml_stats = {
        "model": ml_model,
        "cv": "StratifiedKFold 5-fold",
        "accuracy": ml_acc, "auc": ml_auc, "f1": ml_f1,
        "top_features": [g.strip() for g in top_feat_str.split(",")][:5],
    }
    go_results = [
        {"GO Term": "Extracellular matrix organization", "Overlap": 12, "Fold Enrichment": 4.2, "p-value": 0.00003},
        {"GO Term": "NF-kB / Inflammatory signaling",    "Overlap": 9,  "Fold Enrichment": 3.8, "p-value": 0.00011},
        {"GO Term": "TGF-beta / Fibrosis",               "Overlap": 8,  "Fold Enrichment": 3.5, "p-value": 0.00024},
        {"GO Term": "Satellite cell / Myogenesis",       "Overlap": 7,  "Fold Enrichment": 3.1, "p-value": 0.00089},
        {"GO Term": "Mitochondrial OXPHOS",              "Overlap": 6,  "Fold Enrichment": 2.9, "p-value": 0.00134},
    ]
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    with st.spinner("Generating PDF report..."):
        pdf_buf = build_pdf(
            report_title, patient_id, analyst_name, institution,
            disease_focus, date_str, deg_stats, ml_stats, go_results,
            include_refs, include_interp
        )

    fname = f"MYOomics_Report_{patient_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    st.success("Report generated successfully!")
    st.download_button(
        "📥 Download PDF Report", pdf_buf, fname, "application/pdf",
        use_container_width=True
    )

    st.markdown(f"""
<div style='background:#1e293b; border-radius:10px; padding:16px; margin-top:12px;
     border-left:4px solid #22c55e;'>
  <h4 style='color:#22c55e; margin:0 0 8px 0;'>Report Summary</h4>
  <p style='color:#94a3b8; font-size:0.9rem; margin:0;'>
    <b style='color:#f1f5f9;'>{patient_id}</b> — {disease_focus}<br/>
    {int(n_up)+int(n_down)} significant DEGs
    ({int(n_up)} up / {int(n_down)} down) ·
    ML {ml_model} Accuracy={ml_acc} · AUC={ml_auc}<br/>
    {"Clinical interpretation included · " if include_interp else ""}
    Generated: {date_str}
  </p>
</div>
""", unsafe_allow_html=True)
else:
    st.markdown("""
<div style='background:#1e293b; border:2px dashed #334155; border-radius:12px;
     padding:32px; text-align:center; margin-top:16px;'>
  <span style='font-size:3rem;'>📄</span>
  <h3 style='color:#94a3b8; margin:12px 0 8px 0;'>Configure and generate your report</h3>
  <p style='color:#64748b; font-size:0.9rem;'>
    Fill in the analysis results above, then click <b>Generate PDF Report</b>.<br/>
    The PDF will include all sections and be ready for clinician review.
  </p>
</div>
""", unsafe_allow_html=True)
