# Run MYOomics Locally

Launch the MYOomics Streamlit app in local development mode.

Execute:
```bash
cd "/Users/tall/Claude Code/MYOomics_SaaS"
streamlit run app.py
```

Before running:
1. Check if required packages are installed: `pip list | grep -E "streamlit|pandas|numpy|plotly|scikit-learn|xgboost|pydeseq2|scanpy"`
2. If missing packages: `pip install -r requirements.txt`
3. Then launch the app

The app should open at http://localhost:8501
If port 8501 is busy, Streamlit will auto-assign the next available port.

If there are import errors, report which package is missing and the fix command.
