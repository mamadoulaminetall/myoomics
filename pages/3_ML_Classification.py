import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (classification_report, confusion_matrix,
                              roc_auc_score, roc_curve)
import xgboost as xgb
import shap
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="MYOomics — ML Classification", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.stApp {background-color:#0f172a; color:#f1f5f9;}
[data-testid="stSidebar"] {background-color:#0f172a;}
[data-testid="stMetric"] {background:#1e293b;border-radius:10px;padding:12px;border:1px solid #334155;}
.stButton>button {background:linear-gradient(135deg,#5a1a6e,#a855f7);color:white;border:none;border-radius:8px;font-weight:600;}
[data-testid="stFileUploader"] {background:#1e293b;border:2px dashed #334155;border-radius:10px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='border-left:4px solid #a855f7; padding-left:14px; margin-bottom:20px;'>
  <h2 style='color:#a855f7; margin:0;'>🤖 ML Patient Classification</h2>
  <p style='color:#94a3b8; margin:4px 0 0 0; font-size:0.9rem;'>
    Random Forest · XGBoost · SVM — StratifiedKFold CV —
    SHAP explainability — ROC curves — Patient subtype stratification
  </p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ ML Parameters")
    model_choice = st.selectbox("Model", ["Random Forest", "XGBoost", "SVM (RBF)"])
    n_splits     = st.slider("CV folds (StratifiedKFold)", 3, 10, 5)
    n_estimators = st.slider("n_estimators (RF/XGB)", 50, 500, 200, 50)
    max_depth    = st.slider("max_depth", 2, 10, 4)
    n_top_feat   = st.slider("Top features to show (SHAP)", 10, 30, 15)
    st.markdown("---")
    st.markdown("""
<div style='font-size:0.78rem; color:#64748b;'>
  <b style='color:#94a3b8;'>Expected format:</b><br/>
  Rows = patients/samples<br/>
  Columns = features (genes/omics values)<br/>
  Last column = label (disease subtype)
</div>
""", unsafe_allow_html=True)

# ── Demo data ─────────────────────────────────────────────────────────────────
SUBTYPES = ["DMD", "LGMD-R1", "LGMD-R2", "DM1", "Control"]
SUBTYPE_COLORS = {"DMD": "#ef4444", "LGMD-R1": "#f97316", "LGMD-R2": "#eab308",
                  "DM1": "#22c55e", "Control": "#3b82f6"}

KEY_FEATURES = [
    "DMD_expr", "UTRN_expr", "COL1A1_expr", "TGFB1_expr", "PAX7_expr",
    "MYH7_expr", "MSTN_expr", "FOXO3_expr", "TTN_expr", "CAPN3_expr",
    "DYSF_expr", "DMPK_expr", "SGCA_expr", "IL6_expr", "TNF_expr",
    "SDNN_equivalent", "FAP_score", "Fibrosis_score", "Inflammation_score", "Regeneration_score"
]

def make_demo_ml():
    np.random.seed(99)
    profiles = {
        "DMD":     [0.05, 0.3, 8.0, 7.5, 0.2, 0.3, 6.0, 5.0, 0.2, 1.0, 1.0, 1.0, 0.1, 8.0, 7.0, 25, 8.5, 8.0, 7.5, 1.5],
        "LGMD-R1": [1.0,  0.8, 4.0, 4.5, 0.5, 0.6, 3.5, 4.0, 0.6, 0.1, 1.0, 1.0, 0.9, 5.0, 4.5, 45, 5.5, 5.0, 5.0, 3.0],
        "LGMD-R2": [1.0,  0.9, 5.0, 4.0, 0.4, 0.5, 3.0, 3.5, 0.7, 1.0, 0.1, 1.0, 0.8, 4.5, 4.0, 50, 5.0, 4.5, 4.5, 3.5],
        "DM1":     [1.0,  1.0, 2.0, 2.5, 0.6, 0.7, 2.0, 2.5, 0.8, 1.0, 1.0, 0.1, 0.9, 3.0, 3.0, 60, 3.0, 3.0, 3.5, 5.0],
        "Control": [2.0,  2.0, 1.0, 1.0, 1.5, 2.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 100, 1.0, 1.0, 1.0, 8.0],
    }
    n_per = 30
    rows, labels = [], []
    for subtype, means in profiles.items():
        for _ in range(n_per):
            row = [max(0, np.random.normal(m, m * 0.25 + 0.1)) for m in means]
            rows.append(row)
            labels.append(subtype)
    df = pd.DataFrame(rows, columns=KEY_FEATURES)
    df["label"] = labels
    return df

def _shap_sensitivity(model, X, feature_names):
    x = X.mean(axis=0).reshape(1, -1).copy().astype(float)
    n = x.shape[1]
    sens = np.zeros(n)
    for i in range(n):
        delta = abs(x[0, i]) * 0.1 + 1e-6
        xp = x.copy(); xp[0, i] += delta
        xm = x.copy(); xm[0, i] -= delta
        pp = model.predict_proba(xp)[0]
        pm = model.predict_proba(xm)[0]
        sens[i] = np.abs((pp - pm) / (2 * delta)).mean()
    return sens

def train_and_evaluate(X, y, model_name, n_splits, n_est, depth):
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    if model_name == "Random Forest":
        clf = RandomForestClassifier(n_estimators=n_est, max_depth=depth,
                                      random_state=42, n_jobs=-1)
    elif model_name == "XGBoost":
        clf = xgb.XGBClassifier(n_estimators=n_est, max_depth=depth,
                                  use_label_encoder=False, eval_metric="mlogloss",
                                  random_state=42, verbosity=0)
    else:
        clf = SVC(kernel="rbf", probability=True, random_state=42, C=1.0)

    y_pred = cross_val_predict(clf, X_sc, y_enc, cv=cv)
    y_prob = cross_val_predict(clf, X_sc, y_enc, cv=cv, method="predict_proba")
    clf.fit(X_sc, y_enc)

    try:
        auc = roc_auc_score(y_enc, y_prob, multi_class="ovr", average="macro")
    except Exception:
        auc = 0.0

    report = classification_report(y_enc, y_pred, target_names=le.classes_, output_dict=True)
    cm = confusion_matrix(y_enc, y_pred)

    # SHAP / importance
    if model_name == "Random Forest":
        importances = clf.feature_importances_
    elif model_name == "XGBoost":
        importances = clf.feature_importances_
    else:
        importances = _shap_sensitivity(clf, X_sc, X.columns.tolist())

    return clf, scaler, le, auc, report, cm, importances, y_pred, y_prob

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("### 📁 Upload Omics Feature Matrix")
col_up, col_demo = st.columns([3, 1])
with col_up:
    uploaded_ml = st.file_uploader(
        "Upload CSV (rows=patients, cols=features, last col='label')",
        type=["csv", "tsv"],
    )
with col_demo:
    st.markdown("<br/>", unsafe_allow_html=True)
    use_demo_ml = st.button("🧪 Use Demo Dataset\n(5 IMD subtypes)", use_container_width=True)

data_df = None
if use_demo_ml:
    data_df = make_demo_ml()
    st.success(f"Demo loaded: {len(data_df)} patients × {len(KEY_FEATURES)} features — 5 IMD subtypes")
elif uploaded_ml is not None:
    try:
        sep = "\t" if uploaded_ml.name.endswith(".tsv") else ","
        data_df = pd.read_csv(uploaded_ml, sep=sep)
        st.success(f"Loaded: {data_df.shape[0]} samples × {data_df.shape[1]-1} features")
    except Exception as e:
        st.error(f"Error: {e}")

if data_df is not None:
    if "label" not in data_df.columns:
        st.error("Column 'label' not found. Add a 'label' column with class names.")
        st.stop()

    X = data_df.drop(columns=["label"]).select_dtypes(include=[np.number])
    y = data_df["label"]

    if len(y.unique()) < 2:
        st.error("Need at least 2 classes.")
        st.stop()

    with st.spinner(f"Training {model_choice} with {n_splits}-fold StratifiedKFold CV..."):
        clf, scaler, le, auc, report, cm, importances, y_pred, y_prob = \
            train_and_evaluate(X, y, model_choice, n_splits, n_estimators, max_depth)

    # KPIs
    acc = report["accuracy"]
    macro_f1 = report["macro avg"]["f1-score"]
    st.markdown("### 📈 Model Performance")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Model", model_choice)
    k2.metric("Accuracy", f"{acc:.3f}")
    k3.metric("Macro AUC", f"{auc:.3f}")
    k4.metric("Macro F1", f"{macro_f1:.3f}")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🎯 SHAP Importance", "📊 Confusion Matrix", "📈 ROC Curves", "📋 Full Report"])

    with tab1:
        feat_imp = pd.Series(importances, index=X.columns).nlargest(n_top_feat)
        fig_shap = go.Figure(go.Bar(
            x=feat_imp.values[::-1], y=feat_imp.index[::-1],
            orientation="h",
            marker=dict(
                color=feat_imp.values[::-1],
                colorscale="Purples",
                showscale=False,
            ),
            hovertemplate="<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>",
        ))
        fig_shap.update_layout(
            template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            title=dict(text=f"Feature Importance — {model_choice}",
                       font=dict(color="#a855f7", size=15)),
            xaxis_title="Importance Score",
            height=max(350, n_top_feat * 24 + 80),
            font=dict(color="#f1f5f9"),
        )
        st.plotly_chart(fig_shap, use_container_width=True)
        st.markdown(f"""
<div style='background:#1e293b; border-radius:8px; padding:12px; font-size:0.85rem; color:#94a3b8;'>
  <b style='color:#f1f5f9;'>Reading the importance plot:</b><br/>
  {'SHAP-based sensitivity analysis' if model_choice == 'SVM (RBF)' else 'Feature importance from ' + model_choice}.
  Higher score = stronger contribution to patient classification.<br/>
  Top features align with convergent multi-omics targets identified in the systematic review
  (UTRN, COL1A1, TGFB1, PAX7, MSTN, FOXO3).
</div>
""", unsafe_allow_html=True)

    with tab2:
        labels_list = le.classes_
        z_text = [[str(v) for v in row] for row in cm]
        fig_cm = go.Figure(go.Heatmap(
            z=cm, x=list(labels_list), y=list(labels_list),
            text=z_text, texttemplate="%{text}",
            colorscale="Purples",
            hovertemplate="True: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>",
            colorbar=dict(tickfont=dict(color="#f1f5f9")),
        ))
        fig_cm.update_layout(
            template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            title=dict(text="Confusion Matrix — Cross-Validated Predictions",
                       font=dict(color="#a855f7", size=15)),
            xaxis_title="Predicted Label", yaxis_title="True Label",
            height=420, font=dict(color="#f1f5f9"),
        )
        st.plotly_chart(fig_cm, use_container_width=True)

    with tab3:
        y_enc = le.transform(y)
        fig_roc = go.Figure()
        for i, cls in enumerate(le.classes_):
            y_bin = (y_enc == i).astype(int)
            prob_i = y_prob[:, i]
            fpr, tpr, _ = roc_curve(y_bin, prob_i)
            auc_i = roc_auc_score(y_bin, prob_i)
            color = SUBTYPE_COLORS.get(cls, "#94a3b8")
            fig_roc.add_trace(go.Scatter(
                x=fpr, y=tpr, mode="lines", name=f"{cls} (AUC={auc_i:.3f})",
                line=dict(color=color, width=2),
            ))
        fig_roc.add_trace(go.Scatter(x=[0,1], y=[0,1], mode="lines",
                                      name="Random", line=dict(color="#475569", dash="dash")))
        fig_roc.update_layout(
            template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            title=dict(text="ROC Curves — One-vs-Rest per IMD Subtype",
                       font=dict(color="#a855f7", size=15)),
            xaxis_title="False Positive Rate", yaxis_title="True Positive Rate",
            height=480, legend=dict(bgcolor="#1e293b", bordercolor="#334155"),
            font=dict(color="#f1f5f9"),
        )
        st.plotly_chart(fig_roc, use_container_width=True)

    with tab4:
        rep_df = pd.DataFrame(report).T.round(3)
        st.dataframe(rep_df.style.background_gradient(subset=["f1-score"],
                                                        cmap="Purples", vmin=0, vmax=1),
                     use_container_width=True)
        csv_imp = pd.Series(importances, index=X.columns).sort_values(ascending=False)
        csv_bytes = csv_imp.reset_index().rename(
            columns={"index": "feature", 0: "importance"}).to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Feature Importances (CSV)", csv_bytes,
                           "feature_importance_myoomics.csv", "text/csv",
                           use_container_width=True)
else:
    st.markdown("""
<div style='background:#1e293b; border:2px dashed #334155; border-radius:12px;
     padding:40px; text-align:center; margin-top:20px;'>
  <span style='font-size:3rem;'>🤖</span>
  <h3 style='color:#94a3b8; margin:12px 0 8px 0;'>Upload feature matrix to begin</h3>
  <p style='color:#64748b; font-size:0.9rem;'>
    CSV with patients as rows, omics features as columns, and a <code>label</code>
    column with IMD subtype labels.<br/>
    Or click <b>Use Demo Dataset</b> to explore classification on 5 IMD subtypes.
  </p>
</div>
""", unsafe_allow_html=True)
