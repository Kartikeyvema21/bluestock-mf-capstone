# Mutual Fund Analytics Platform

A comprehensive analytics system for mutual funds including ETL pipeline, data cleaning, SQLite star schema, performance metrics, fund ranking, recommendation engine, and Power BI dashboard.

---

## ✅ Completed & Pushed to GitHub

### Day 1 – Project Setup & Data Ingestion
- Created project folder structure (`data/raw/`, `data/processed/`, `data/db/`, `notebooks/`, `scripts/`, `sql/`, `dashboard/`, `reports/`).
- Set up `requirements.txt` with pandas, numpy, sqlalchemy, plotly, jupyter, etc.
- Built `data_ingestion.py` – reads raw CSV files, standardises column names, validates NAV and date, and saves merged data to `data/processed/`.
- Generated sample mutual fund CSV files (`nav_history.csv`, `investor_transactions.csv`, `scheme_performance.csv`) using `generate_day2_data.py`.

### Day 2 – Data Cleaning & SQL Database Design
- **Cleaning scripts:**
  - `clean_nav_history.py` – parsed dates, sorted by fund+date, forward-filled missing NAV (weekends/holidays), removed duplicates, validated NAV>0.
  - `clean_investor_transactions.py` – standardised transaction types (SIP/Lumpsum/Redemption), validated positive amounts, fixed date formats, checked KYC status.
  - `clean_scheme_performance.py` – ensured numeric returns, flagged anomalies, validated expense ratio range (0.1–2.5%).
- **SQLite star schema:**
  - `schema.sql` – created dimension tables (`dim_fund`, `dim_date`) and fact tables (`fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`) with primary/foreign keys.
  - `load_to_sqlite.py` – loaded cleaned CSVs into SQLite, handling surrogate keys and referential integrity.
- **Analytical SQL queries:**
  - `queries.sql` – 10 business queries (top funds by AUM, average NAV per month, SIP YoY growth, transactions by state, low‑expense funds, volatility, redemption %, KYC by city, fund ranking, return vs expense).
- **Data dictionary:**
  - `data_dictionary.md` – documented all columns, data types, business definitions, and validation rules.

### Day 3 – Exploratory Data Analysis (EDA)
- **Expanded to 40 schemes** – simulated realistic NAV data (2022–2025) to enable rich analysis.
- **NAV trend analysis** – daily NAV for all 40 schemes with shaded regions for 2023 bull run and 2024 market corrections (Plotly).
- **AUM growth bar chart** – grouped bar by fund house (HDFC, SBI, ICICI, Axis, Kotak) for 2022–2025; highlighted SBI ₹12.5 lakh crore dominance (Plotly).
- **SIP inflow time‑series** – monthly SIP trend (Jan 2022 – Dec 2025) with annotation of ₹31,002 Cr all-time high (Dec 2025) (Plotly).
- **Category inflow heatmap** – months vs fund categories (Large Cap, Mid Cap, Small Cap, Hybrid); net inflow as colour intensity (Seaborn).
- **Investor demographics** – age group distribution pie chart, SIP amount box plot by age group, gender split pie chart (Plotly).
- **Geographic distribution** – horizontal bar chart of SIP amount by state; T30 vs B30 city tier pie chart (Plotly).
- **Folio count growth** – line chart from 13.26 Cr (Jan 2022) to 26.12 Cr (Dec 2025) with key milestones annotated (Plotly).
- **NAV return correlation matrix** – pairwise correlation of daily returns for 10 selected funds (Seaborn heatmap).
- **Sector allocation donut** – aggregate sector weights (Financial Services, IT, Healthcare, etc.) across all equity funds (Plotly).
- **10 key EDA findings** – documented in notebook markdown cells, each with a supporting chart reference.
- **Deliverables:** `notebooks/03_eda_analysis.ipynb` (fully executable) and 15+ interactive HTML/PNG charts saved to `reports/eda_plots/`.

---

## 📁 Current Folder Structure (pushed)
