
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from io import BytesIO

# PAGE CONFIG - LIGHT THEME
st.set_page_config(page_title="MediCore AI BI Agent", page_icon="💊", layout="wide")

# LIGHT THEME CSS - No dark backdrop
st.markdown("""
<style>
.stApp { background: #f8fafc !important; }
section[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e2e8f0; }
h1, h2, h3, p, label, .stMarkdown { color: #0f172a !important; }
div[data-testid="stMetric"] { background: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.stDownloadButton button, .stButton button { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# FIX 1: API KEY - NEVER hardcode raw key without quotes
def get_api_key():
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except:
        pass
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except:
        pass
    return os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY") or None

API_KEY = get_api_key()

# Helper for new streamlit width API
def get_width_params():
    # Streamlit >= 1.36 uses width='stretch', old uses use_container_width
    try:
        # test new param
        return {"width": "stretch"}
    except:
        return {"use_container_width": True}

# Sample data loader
@st.cache_data
def load_sample(name):
    # In production, these are in repo /data folder
    # For demo, generate if not exists
    if name == "healthcare_sales.csv":
        return pd.read_csv("sample_data/healthcare_sales.csv") if os.path.exists("sample_data/healthcare_sales.csv") else pd.DataFrame()
    return pd.DataFrame()

# SIDEBAR
with st.sidebar:
    st.title("📁 Sample Files Included")
    st.markdown("""
    - healthcare_sales.csv
    - pharma_inventory.csv  
    - hospital_metrics.csv
    """)
    
    # Download sample files
    if os.path.exists("sample_data/healthcare_sales.csv"):
        for fname in ["healthcare_sales.csv","pharma_inventory.csv","hospital_metrics.csv"]:
            path = f"sample_data/{fname}"
            if os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button(f"⬇️ Download {fname}", f, file_name=fname, mime="text/csv", key=f"dl_{fname}")

    st.divider()
    st.subheader("Upload your business CSV")
    uploaded = st.file_uploader("Upload", type=["csv","xlsx","xls"], label_visibility="collapsed")
    
    if uploaded:
        try:
            if uploaded.name.endswith('.csv'):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
            st.session_state['df'] = df
            st.success(f"Loaded {len(df)} rows, {len(df.columns)} cols")
        except Exception as e:
            st.error(f"Upload error: {e}")

    if st.button("🎯 Load Demo (500 Records)", type="primary", use_container_width=True):
        np.random.seed(42)
        df_demo = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=500),
            'Product': np.random.choice(['Paracetamol','Amoxicillin','Metformin','Atorvastatin'], 500),
            'Region': np.random.choice(['North','South','East','West'], 500),
            'Sales': np.random.randint(5000, 50000, 500),
            'Profit': np.random.randint(500, 8000, 500),
            'Quantity': np.random.randint(10, 500, 500)
        })
        st.session_state['df'] = df_demo

# MAIN
st.title("💬 AI BI Agent — Natural Language Query")
st.caption("Ask anything about your uploaded file, or generate SQL queries, visualizations, and reports.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Top Products", use_container_width=True): st.session_state['q'] = "Show total sales by Product with bar chart and give business insights"
with col2:
    if st.button("Monthly Trend", use_container_width=True): st.session_state['q'] = "Show monthly sales trend line chart"
with col3:
    if st.button("Region Compare", use_container_width=True): st.session_state['q'] = "Compare sales by Region"
with col4:
    if st.button("Margin Leakage", use_container_width=True): st.session_state['q'] = "Find products with low profit margin"

query = st.text_input("Your question", value=st.session_state.get('q',''), placeholder="Show total sales by Product with bar chart and give business insights")

if st.button("🚀 Run Agent", type="primary", use_container_width=True):
    df = st.session_state.get('df')
    if df is None:
        st.warning("👈 Please load demo data or upload CSV/Excel first from sidebar")
    else:
        with st.spinner("MediCore AI is analyzing..."):
            # Show basic analytics (works without API key)
            st.subheader("📊 Analytics")
            numeric_df = df.select_dtypes(include=[np.number])
            
            c1, c2, c3 = st.columns(3)
            if 'Sales' in df.columns:
                c1.metric("Total Sales", f"₹{df['Sales'].sum():,}")
            if 'Profit' in df.columns:
                c2.metric("Total Profit", f"₹{df['Profit'].sum():,}")
            if 'Profit' in df.columns and 'Sales' in df.columns:
                margin = (df['Profit'].sum()/df['Sales'].sum()*100) if df['Sales'].sum()!=0 else 0
                c3.metric("Margin %", f"{margin:.1f}%")
            
            # Charts
            if 'Product' in df.columns and 'Sales' in df.columns:
                fig = px.bar(df.groupby('Product')['Sales'].sum().reset_index(), x='Product', y='Sales', title="Sales by Product", color='Sales')
                st.plotly_chart(fig, use_container_width=True)
            
            if not numeric_df.empty and numeric_df.shape[1] >= 2:
                st.subheader("Correlation Heatmap")
                corr = numeric_df.corr()
                fig2 = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
                fig2.update_layout(height=500)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Business Insights (FIXED - no NameError)
            st.subheader("💡 Business Insights")
            try:
                insights = []
                if 'Sales' in df.columns:
                    top_prod = df.groupby('Product')['Sales'].sum().sort_values(ascending=False).head(1)
                    if not top_prod.empty:
                        insights.append(f"• Top performing product is **{top_prod.index[0]}** with ₹{top_prod.values[0]:,} sales")
                if 'Region' in df.columns and 'Sales' in df.columns:
                    top_reg = df.groupby('Region')['Sales'].sum().sort_values(ascending=False).head(1)
                    if not top_reg.empty:
                        insights.append(f"• Strongest region is **{top_reg.index[0]}**")
                if 'Profit' in df.columns and 'Sales' in df.columns:
                    df['Margin'] = df['Profit']/df['Sales']
                    low_margin = df.groupby('Product')['Margin'].mean().sort_values().head(1)
                    if not low_margin.empty and low_margin.values[0] < 0.15:
                        insights.append(f"• Margin leakage in **{low_margin.index[0]}** ({low_margin.values[0]*100:.1f}% margin) - review pricing")
                if not insights:
                    insights.append("• Data looks balanced. Upload more history for deeper trends.")
                for ins in insights:
                    st.markdown(ins)
            except Exception as e:
                st.error(f"Insights error: {e}")
            
            # FIX 2: Export - Both CSV and Excel
            st.subheader("📤 Export These Analytics")
            col_a, col_b = st.columns(2)
            with col_a:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Download Full Dataset CSV", csv, "export.csv", "text/csv", use_container_width=True)
            with col_b:
                # Excel export
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Data')
                    if 'Sales' in df.columns and 'Product' in df.columns:
                        df.groupby('Product')['Sales'].sum().reset_index().to_excel(writer, index=False, sheet_name='Summary')
                excel_data = output.getvalue()
                st.download_button("⬇️ Download Excel (XLSX)", excel_data, "export.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            
            # AI Insights if API key present
            if API_KEY:
                st.info("AI Agent would generate SQL + deeper insights here with your API key")
            else:
                st.warning("Add OPENAI_API_KEY or GOOGLE_API_KEY in Streamlit Secrets to enable AI natural language queries")
