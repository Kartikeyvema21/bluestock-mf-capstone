# Mutual Fund Analytics Platform

A comprehensive analytics system for mutual funds including ETL pipeline, data cleaning, SQLite star schema, exploratory data analysis (EDA), performance metrics (CAGR, Sharpe, Beta, VaR), fund ranking, recommendation engine, and Power BI dashboard.

---

## ✅ Completed & Pushed to GitHub

### Day 1 – Project Setup & Data Ingestion
- Created project folder structure (`data/raw/`, `data/processed/`, `data/db/`, `notebooks/`, `scripts/`, `sql/`, `dashboard/`, `reports/`).
- Set up `requirements.txt` with pandas, numpy, sqlalchemy, plotly, jupyter, etc.
- Built `data_ingestion.py` – reads raw CSV files, standardises column names, validates NAV and date, and saves merged data to `data/processed/`.
- Generated sample mutual fund CSV files (`nav_history.csv`, `investor_transactions.csv`, `scheme_performance.csv`) using `generate_day2_data.py`.

### Day 2 – Data Cleaning & SQL Database Design
- **Cleaning scripts:**
  - `clean_nav_history.py` – parsed dates, sorted by fund+date, forward‑filled missing NAV (weekends/holidays), removed duplicates, validated NAV>0.
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
- Expanded to 40 schemes – simulated realistic NAV data (2022–2025) to enable rich analysis.
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

### Day 4 – Fund Performance Analytics
- **Daily returns** – computed `daily_return = nav_t / nav_{t-1} − 1` for all 40 funds; validated distribution (histogram).
- **CAGR (1yr, 3yr, 5yr)** – `CAGR = (NAV_end / NAV_start)^(1/n) − 1`; built comparison table across all funds → `cagr_results.csv`.
- **Sharpe Ratio** – `(Rp − Rf) / Std(Rp) × √252` with Rf = 6.5% (RBI repo rate proxy); ranked 40 funds → `sharpe_ratios.csv` + top‑20 bar chart.
- **Sortino Ratio** – same formula but denominator uses only downside standard deviation (negative returns only) → `sortino_ratios.csv`.
- **Alpha & Beta** – OLS regression of fund returns on Nifty 100 returns using `scipy.stats.linregress`; Alpha = intercept × 252 → `alpha_beta.csv`.
- **Maximum Drawdown** – `min(NAV / running_max − 1)` for each fund; worst drawdown date range identified → `max_drawdown.csv`.
- **Fund Scorecard (0–100)** – composite: 30% × 3yr return rank + 25% × Sharpe rank + 20% × Alpha rank + 15% × expense ratio rank (inverse) + 10% × max DD rank (inverse) → `fund_scorecard.csv`.
- **Benchmark comparison chart** – plotted top 5 funds vs Nifty 50 and Nifty 100 over 3 years; computed tracking error = `std(fund_return − benchmark_return) × √252` → `benchmark_comparison.png/.html` and `tracking_errors.csv`.
- **Deliverables:** `notebooks/04_performance_analytics.ipynb`, `fund_scorecard.csv`, `alpha_beta.csv`, benchmark comparison chart PNG.

---

## 📁 Current Folder Structure (pushed)
