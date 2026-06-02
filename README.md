# Mutual Fund Analytics Platform

A comprehensive analytics system for mutual funds including ETL pipeline, data cleaning, SQLite star schema, performance metrics, fund ranking, recommendation engine, and Power BI dashboard.

## ✅ Completed & Pushed to GitHub

### Day 1 – Project Setup & Data Ingestion

- Created project folder structure (`data/raw/`, `data/processed/`, `data/db/`, `notebooks/`, `scripts/`, `sql/`, `dashboard/`, `reports/`).
- Set up `requirements.txt` with pandas, numpy, sqlalchemy, plotly, jupyter, etc.
- Built `data_ingestion.py` – reads raw CSV files, standardises column names, validates NAV and date, and saves merged data to `data/processed/`.
- Generated sample mutual fund CSV files (`nav_history.csv`, `investor_transactions.csv`, `scheme_performance.csv`) using `generate_day2_data.py`.

### ✅ Day 2 – Data Cleaning & SQL Database Design

- **Cleaning scripts**:
  - `clean_nav_history.py` – parsed dates, sorted by fund+date, forward-filled missing NAV (weekends/holidays), removed duplicates, validated NAV>0.
  - `clean_investor_transactions.py` – standardised transaction types (SIP/Lumpsum/Redemption), validated positive amounts, fixed date formats, checked KYC status.
  - `clean_scheme_performance.py` – ensured numeric returns, flagged anomalies, validated expense ratio range (0.1–2.5%).
- **SQLite star schema**:
  - `schema.sql` – created dimension tables (`dim_fund`, `dim_date`) and fact tables (`fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`) with primary/foreign keys.
  - `load_to_sqlite.py` – loaded cleaned CSVs into SQLite, handling surrogate keys and referential integrity.
- **Analytical SQL queries**:
  - `queries.sql` – 10 business queries (top funds by AUM, average NAV per month, SIP YoY growth, transactions by state, low‑expense funds, volatility, redemption %, KYC by city, fund ranking, return vs expense).
- **Data dictionary**:
  - `data_dictionary.md` – documented all columns, data types, business definitions, and validation rules.

## 📁 Current Folder Structure (pushed)

