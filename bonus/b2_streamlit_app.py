# bonus/b2_streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'db' / 'bluestock_mf.db'

st.set_page_config(layout="wide")
st.title("📊 Mutual Fund Analytics Dashboard")

conn = sqlite3.connect(DB_PATH)

funds = pd.read_sql("SELECT * FROM dim_fund", conn)
nav = pd.read_sql("""
    SELECT f.scheme_name, d.full_date, n.nav
    FROM fact_nav n
    JOIN dim_fund f ON n.fund_key = f.fund_key
    JOIN dim_date d ON n.date_key = d.date_key
""", conn)

selected_fund = st.sidebar.selectbox("Select Fund", funds['scheme_name'].unique())
fund_nav = nav[nav['scheme_name'] == selected_fund]

fig = px.line(fund_nav, x='full_date', y='nav', title=f'NAV History – {selected_fund}')
st.plotly_chart(fig, width='stretch')   # ✅ replaced use_container_width=True

score_path = BASE_DIR / 'data' / 'processed' / 'fund_scorecard.csv'
if score_path.exists():
    score = pd.read_csv(score_path)
    st.subheader("🏆 Fund Scorecard (Top 10)")
    st.dataframe(score.head(10))

conn.close()