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

### Day 5 – Power BI Dashboard
- **Connected Power BI to data** – loaded all cleaned CSVs (`dim_fund`, `dim_date`, `fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`, `fund_scorecard`) via Text/CSV.
- **Created star schema relationships** in Power BI Model view.
- **Page 1 – Industry Overview:** KPI cards (Total AUM ₹81L Cr, SIP Inflows ₹31K Cr, Folios 26.12 Cr, Schemes 1,908), AUM trend line chart (2022–2025), AUM by AMC bar chart.
- **Page 2 – Fund Performance:** Scatter plot (return vs risk, bubble size = AUM), sortable fund scorecard table, NAV line chart with scheme slicer, slicers for fund house, category, and plan, drill‑through to NAV detail page.
- **Page 3 – Investor Analytics:** Bar chart (transaction amount by state), donut chart (SIP/Lumpsum/Redemption split), bar chart (age group vs avg SIP amount), monthly transaction volume line chart, slicers for state, age group, city tier.
- **Page 4 – SIP & Market Trends:** Dual‑axis chart (SIP inflow bar + Nifty 50 line), category inflow heatmap, top 5 categories by net inflow (FY25).
- **Interactivity:** Drill‑through from fund table to NAV detail page, tooltips on all charts, Bluestock colour theme applied, logo added.
- **Export:** `.pbix` file saved in `dashboard/`, PDF exported to `reports/`, 4 page PNG screenshots captured.
- **Deliverables:** `bluestock_mf_dashboard.pbix`, `Dashboard.pdf`, 4 page PNG screenshots.

### Day 6 – Advanced Analytics & Risk Metrics
- **Historical VaR (95%) and CVaR** – computed 5th percentile of daily returns and mean of returns below VaR threshold for all 40 schemes → `var_cvar_report.csv`.
- **Rolling 90‑day Sharpe ratio** – calculated rolling Sharpe for top 5 funds and plotted over time → `rolling_sharpe_chart.png`.
- **Investor cohort analysis** – grouped investors by first transaction year; computed avg SIP amount, total invested, top fund preference per cohort → `cohort_analysis.csv`.
- **SIP continuity analysis** – for investors with 6+ SIP transactions, computed average gap between dates; flagged investors with gap > 35 days as "at‑risk" → `sip_continuity_analysis.csv`.
- **Simple fund recommender** – based on risk appetite (Low / Moderate / High), outputs top 3 funds by Sharpe ratio within matching risk grade → `recommender.py`.
- **Sector HHI concentration** – calculated Herfindahl‑Hirschman Index = Σ(weight_i²) per fund; compared across all equity funds → `sector_hhi.csv`.
- **5 advanced insights** – documented in Jupyter Markdown: highest VaR funds, cohort behaviour, SIP continuity rate, sector HHI, rolling Sharpe trends.
- **Deliverables:** `notebooks/05_advanced_analytics.ipynb`, `var_cvar_report.csv`, `recommender.py`, `rolling_sharpe_chart.png`.

### Day 7 – Final Submission & Documentation
- **Complete Project Documentation**
  - Comprehensive README.md with setup instructions, architecture, and usage guide
  - Data dictionary with all column definitions and business rules
  - Final report covering executive summary, methodology, findings, and recommendations (15-20 pages)
  
- **Master Execution Script**
  - `run_pipeline.py` – orchestrates entire ETL + analytics pipeline
  - Single command to run data ingestion, cleaning, performance metrics, and recommendations
  
- **Power BI Cloud Publishing**
  - Dashboard published to Power BI Service for online access
  - Interactive features maintained in cloud version
  - Shareable link for stakeholder access
  
- **GitHub Repository Finalization**
  - Clean repository structure with proper .gitignore
  - v1.0 tag for final submission
  - All 7 deliverables committed and pushed
  
- **12-Slide Presentation**
  - Problem statement & objectives
  - Data sources & ETL architecture
  - EDA highlights (2 slides)
  - Performance metrics (2 slides)
  - Dashboard walkthrough (2 slides)
  - Key findings & recommendations
  - Thank you & Q&A

### Project Completion Statistics

| Metric | Value |
|--------|-------|
| **Total Python Scripts** | 15+ |
| **Jupyter Notebooks** | 5 (fully executable) |
| **CSV Files Processed** | 34 (8 raw, 26 processed) |
| **Database Tables** | 6 (star schema) |
| **Performance Metrics** | 10+ (CAGR, Sharpe, Alpha, Beta, VaR, etc.) |
| **Visualizations Created** | 20+ (HTML, PNG, interactive) |
| **Power BI Pages** | 4 (fully interactive) |
| **Bonus Challenges** | 5 (B1–B5) |
| **Lines of Code** | ~2,500 |
| **Analysis Period** | 2022–2025 (4 years) |
| **Mutual Funds Analyzed** | 40 schemes |
| **Investor Records** | 5,000+ |

### All 8 Objectives Completed ✅

1. ✅ **Data Pipeline** – Automated ETL from raw CSV to processed data
2. ✅ **Data Cleaning** – Missing values, outliers, validation rules
3. ✅ **SQL Database** – Star schema with dimensions and facts
4. ✅ **Exploratory Analysis** – 15+ visualizations with insights
5. ✅ **Performance Metrics** – 10+ financial calculations
6. ✅ **Interactive Dashboard** – Power BI with 4 pages
7. ✅ **Advanced Analytics** – VaR, cohorts, recommendations
8. ✅ **Documentation** – Complete README + Final Report

### All 7 Deliverables Submitted ✅

1. ✅ **Final_Report.pdf** – 15-20 page comprehensive report
2. ✅ **Bluestock_MF_Presentation.pptx** – 12-slide deck
3. ✅ **Clean GitHub Repository** – With v1.0 tag
4. ✅ **README.md** – Complete project documentation
5. ✅ **run_pipeline.py** – Master execution script
6. ✅ **Power BI Dashboard** – .pbix + cloud link
7. ✅ **All Source Code** – 5 notebooks, 15+ scripts, 34 CSV files

---

## 📁 Current Folder Structure (pushed)



---

## 🚀 Bonus Challenges Implemented (Separate Folder)

- **B1 – Scheduled ETL** – `bonus/b1_scheduled_etl.py` (auto‑fetch NAV from mfapi.in)
- **B2 – Streamlit web app** – `bonus/b2_streamlit_app.py` (alternative to Power BI)
- **B3 – Monte Carlo simulation** – `bonus/b3_monte_carlo.py` (NAV projection with uncertainty bands)
- **B4 – Markowitz Efficient Frontier** – `bonus/b4_markowitz.py` (portfolio optimisation)
- **B5 – Automated HTML email report** – `bonus/b5_email_report.py` (weekly performance summary)

---

## 🎯 How to Run the Complete Pipeline

### Quick Start (One Command)

```bash
# Run entire ETL + analytics pipeline
python run_pipeline.py"## ?? LIVE INTERACTIVE DASHBOARD"  
""  
"[?? Click Here to View Live Power BI Dashboard](https://app.powerbi.com/groups/me/reports/90387003-0d21-419d-86bb-5226795722a0/b4814ddf04a9294668e9?experience=power-bi)"  
""  
"## ?? LIVE INTERACTIVE DASHBOARD"  
""  
"[?? Click Here to View Live Power BI Dashboard](https://app.powerbi.com/groups/me/reports/90387003-0d21-419d-86bb-5226795722a0/aef12d703791c2728236?experience=power-bi)"  
""  
-e "\n\n## ?? LIVE DASHBOARD\n\n[Click here to view live Power BI dashboard](https://app.powerbi.com/groups/me/reports/90387003-0d21-419d-86bb-5226795722a0/b4814ddf04a9294668e9?experience=power-bi)\n"  
