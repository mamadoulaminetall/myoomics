# Add a New Analysis Page to MYOomics

Add a new Streamlit page to the MYOomics SaaS platform.

The user will specify the page name and analysis type. You must:

1. Ask (or infer from context) what the page should do
2. Create the file at: /Users/tall/Claude Code/MYOomics_SaaS/pages/N_PageName.py
   - N = next page number (check existing pages/ directory)
   - Use the MYOomics dark theme (background #0f172a, accent color matching the analysis type)
   - Follow the exact same structure as existing pages (header, sidebar controls, upload + demo button, tabs for results)
3. Add a st.page_link() entry in app.py sidebar navigation
4. Update requirements.txt if new dependencies are needed
5. Update /Users/tall/.claude/projects/-Users-tall-Claude-Code/memory/project_myoomics_saas.md with the new page

Standard page template:
- Dark CSS header block
- Colored left-border header (border-left: 4px solid [color])
- Sidebar with ⚙️ Analysis Parameters
- File uploader + demo button side by side
- KPI metrics row after data load
- st.tabs() for results (plots, tables, downloads)
- Download button in last tab
