# 🧬 MYOomics — Multi-Omics Analysis Platform for Muscular Dystrophies

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://myoomics.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3b82f6.svg)](https://python.org)

> Automated multi-omics analysis platform — Bulk RNA-seq · Single-cell · ML Classification · PDF Reports

---

## Overview

**MYOomics** is an automated SaaS platform for multi-omics analysis in inherited muscular dystrophies (DMD, LGMD, DM1, FSHD). Built on a PRISMA 2020 systematic review of **67 studies / 4,213 samples**, it standardizes RNA-seq, scRNA-seq and ML workflows into reproducible, clinician-ready pipelines.

**Scientific basis:** TALL ML. *Multi-Omics Profiling in Inherited Muscular Dystrophies: A Systematic Review of Transcriptomic, Epigenomic and Proteomic Studies.* medRxiv 2026.

---

## Features

| Module | Capabilities |
|--------|-------------|
| 📊 **Bulk RNA-seq** | DESeq2-based DE analysis, volcano plot, heatmap, GO/KEGG enrichment |
| 🔬 **Single-Cell** | UMAP, Leiden clustering, marker genes, CellChat ligand-receptor |
| 🤖 **ML Classification** | Random Forest, XGBoost, SVM + SHAP explainability, ROC curves |
| 📄 **Report Generator** | One-click PDF clinical reports (ReportLab) |
| 💳 **Pricing** | Academic / Hospital / Biotech / Consulting tiers |

---

## Quick Start

```bash
git clone https://github.com/mamadoulaminetall/myoomics.git
cd myoomics
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501

### Demo datasets (in `data/samples/`)

| File | Description |
|------|-------------|
| `demo_rnaseq_counts.csv` | 500 genes × 12 samples (6 Control / 6 DMD) |
| `demo_ml_features.csv` | 150 patients × 20 features — 5 IMD subtypes |
| `demo_singlecell.csv` | 275 cells × 100 genes — 7 muscle cell populations |

---

## Architecture

```
myoomics/
├── app.py                        # Home page + navigation
├── pages/
│   ├── 1_RNAseq_Bulk.py         # Bulk transcriptomics
│   ├── 2_SingleCell.py           # scRNA-seq / snRNA-seq
│   ├── 3_ML_Classification.py    # ML patient stratification
│   ├── 4_Rapport.py              # PDF report generator
│   └── 5_Abonnement.py           # Pricing & contact
├── core/                         # Shared analysis modules
├── data/samples/                 # Demo datasets
├── .streamlit/config.toml        # Dark theme + upload config
└── requirements.txt
```

---

## Scientific Framework

Three convergent molecular axes in muscular dystrophies (from systematic review):

1. **DAGC disassembly / NF-kB inflammation** — RNA-seq + proteomics
2. **Epigenetic reprogramming toward fibrosis** — ChIP-seq + ATAC-seq
3. **Satellite cell exhaustion** — scRNA-seq + H3K27me3

**Convergent therapeutic targets:** UTRN, MSTN, FOXO3, NRF2 (confirmed across ≥3 omics layers)

---

## Stack

- **Frontend:** Streamlit 1.32+, Plotly, dark theme (`#0f172a`)
- **Transcriptomics:** PyDESeq2, scipy, pandas, numpy
- **Single-cell:** Scanpy, AnnData, umap-learn, leidenalg
- **ML:** scikit-learn, XGBoost, SHAP
- **Reports:** ReportLab

---

## Pricing

| Tier | Price |
|------|-------|
| Academic | 2,000–5,000 €/year |
| Hospital / CHU | 8,000–15,000 €/year |
| Biotech / Pharma | 25,000–60,000 €/year |
| Consulting | 800–1,500 €/day |

Contact: mamadoulaminetallgithub@gmail.com

---

## Author

**Dr. Mamadou Lamine TALL, PhD**  
Bioinformatics & AI Applied to Biomedical Research  
Aix-Marseille Université — PhyMedExp, Montpellier  
[github.com/mamadoulaminetall](https://github.com/mamadoulaminetall) · [Google Scholar](https://scholar.google.com/citations?user=qJaCV7MAAAAJ)

---

## License

MIT License — open-source core modules. SaaS platform features require subscription.
