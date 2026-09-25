# MediCore AI BI Agent - FIXED LIGHT VERSION
Author: Anix Lynch

## Bugs Fixed:
1. Dark backdrop -> Light theme (#f8fafc) - text now visible
2. NameError: name 'AQ' is not defined -> Fixed openai_key = st.secrets["OPENAI_API_KEY"]
3. use_container_width=True deprecated -> width="stretch"
4. Export CSV only -> Added CSV + Excel (XLSX) with Summary sheet
5. Upload failing -> Now supports CSV, XLSX, XLS

## Files:
- app_fixed_light.py -> rename to app.py
- sample_data/ -> 3 sample CSVs
- requirements.txt

## Deploy:
1. Copy app_fixed_light.py to app.py in your repo prashantjt77/ai-bi-agent
2. Copy sample_data folder to repo root
3. Push to main
4. Add Secrets in Streamlit Cloud: OPENAI_API_KEY or GOOGLE_API_KEY
5. Your URL: https://ai-bi-agent-zgmlhgvel7kvl6ndbgehpz.streamlit.app will be light and working

## Secrets format:
OPENAI_API_KEY = "sk-proj-..."
GOOGLE_API_KEY = "AIzaSy..."
