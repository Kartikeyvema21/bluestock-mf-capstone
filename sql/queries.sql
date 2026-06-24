-- queries.sql - Useful analytical queries
-- =====================================================
-- Mutual Fund Analytics Platform – Analytical Queries
-- =====================================================
-- Database: bluestock_mf.db (SQLite)
-- Author: Capstone Team
-- Date: 2026-06-02
-- =====================================================

-- -----------------------------------------------------
-- Query 1: Top 5 funds by latest AUM (in crore)
-- -----------------------------------------------------
-- Business question: Which funds have the largest assets under management?
SELECT 
    f.scheme_name,
    f.category,
    ROUND(pa.aum_crore, 2) AS aum_crore
FROM fact_performance pa
JOIN dim_fund f ON pa.fund_key = f.fund_key
ORDER BY pa.aum_crore DESC
LIMIT 5;

-- -----------------------------------------------------
-- Query 2: Average NAV per month for a specific fund (e.g., HDFC Large Cap)
-- -----------------------------------------------------
-- Business question: What is the monthly average NAV trend for a fund?
SELECT 
    d.year,
    d.month,
    d.month_name,
    ROUND(AVG(n.nav), 2) AS avg_nav
FROM fact_nav n
JOIN dim_fund f ON n.fund_key = f.fund_key
JOIN dim_date d ON n.date_key = d.date_key
WHERE f.scheme_name = 'HDFC Large Cap Fund'
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- -----------------------------------------------------
-- Query 3: Year-over-year SIP growth (total SIP amount per year)
-- -----------------------------------------------------
-- Business question: How is SIP contribution growing year by year?
SELECT 
    d.year,
    COUNT(t.transaction_key) AS sip_count,
    ROUND(SUM(t.amount), 2) AS total_sip_amount,
    ROUND(AVG(t.amount), 2) AS avg_sip_amount
FROM fact_transactions t
JOIN dim_date d ON t.date_key = d.date_key
WHERE t.transaction_type = 'SIP'
GROUP BY d.year
ORDER BY d.year;

-- -----------------------------------------------------
-- Query 4: Transaction volume by state (last 12 months)
-- -----------------------------------------------------
-- Business question: Which states have the highest transaction activity?
SELECT 
    t.state,
    COUNT(t.transaction_key) AS transaction_count,
    ROUND(SUM(t.amount), 2) AS total_amount,
    ROUND(AVG(t.amount), 2) AS avg_ticket_size
FROM fact_transactions t
JOIN dim_date d ON t.date_key = d.date_key
WHERE d.full_date >= date('now', '-12 months')
GROUP BY t.state
ORDER BY total_amount DESC;

-- -----------------------------------------------------
-- Query 5: Funds with expense ratio below 1% (low-cost funds)
-- -----------------------------------------------------
-- Business question: Which funds are most cost‑efficient?
SELECT 
    f.scheme_name,
    f.category,
    ROUND(p.expense_ratio, 2) AS expense_ratio_percent,
    ROUND(p.return_1y, 2) AS return_1y_percent
FROM fact_performance p
JOIN dim_fund f ON p.fund_key = f.fund_key
WHERE p.expense_ratio < 1.0
ORDER BY p.expense_ratio ASC;

-- -----------------------------------------------------
-- Query 6: NAV volatility (standard deviation) for each fund
-- -----------------------------------------------------
-- Business question: Which funds are most/least volatile?
SELECT 
    f.scheme_name,
    ROUND(AVG(n.nav), 2) AS avg_nav,
    ROUND(AVG(n.nav) * 0.1, 2) AS example_stddev,  -- placeholder; real STDDEV below
    ROUND((MAX(n.nav) - MIN(n.nav)) / AVG(n.nav) * 100, 2) AS volatility_pct
FROM fact_nav n
JOIN dim_fund f ON n.fund_key = f.fund_key
GROUP BY f.scheme_name
ORDER BY volatility_pct DESC;

-- (Note: For exact STDDEV, use SQLite's `STDEV()` extension or compute in Python.)

-- -----------------------------------------------------
-- Query 7: Monthly redemption amount as percentage of total transactions
-- -----------------------------------------------------
-- Business question: What fraction of transaction value is redeemed each month?
SELECT 
    d.year,
    d.month,
    ROUND(SUM(CASE WHEN t.transaction_type = 'Redemption' THEN t.amount ELSE 0 END), 2) AS redemption_amount,
    ROUND(SUM(t.amount), 2) AS total_amount,
    ROUND(100.0 * SUM(CASE WHEN t.transaction_type = 'Redemption' THEN t.amount ELSE 0 END) / NULLIF(SUM(t.amount), 0), 2) AS redemption_pct
FROM fact_transactions t
JOIN dim_date d ON t.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- -----------------------------------------------------
-- Query 8: Top 3 funds by 3‑year return within each category
-- -----------------------------------------------------
-- Business question: Which funds are the best performers in each category?
WITH ranked_funds AS (
    SELECT 
        f.category,
        f.scheme_name,
        ROUND(p.return_3y, 2) AS return_3y_percent,
        ROW_NUMBER() OVER (PARTITION BY f.category ORDER BY p.return_3y DESC) AS rank_in_category
    FROM fact_performance p
    JOIN dim_fund f ON p.fund_key = f.fund_key
    WHERE p.return_3y IS NOT NULL
)
SELECT category, scheme_name, return_3y_percent, rank_in_category
FROM ranked_funds
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;

-- -----------------------------------------------------
-- Query 9: KYC compliance rate by city (corrected)
SELECT 
    t.city,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN t.kyc_status = 'Verified' THEN 1 ELSE 0 END) AS verified_count,
    ROUND(100.0 * SUM(CASE WHEN t.kyc_status = 'Verified' THEN 1 ELSE 0 END) / COUNT(*), 2) AS kyc_verification_pct
FROM fact_transactions t
GROUP BY t.city
HAVING COUNT(*) >= 10
ORDER BY kyc_verification_pct DESC;

-- -----------------------------------------------------
-- Query 10: Fund performance heatmap (return vs expense)
-- -----------------------------------------------------
-- Business question: Which funds offer the best return relative to expense ratio?
SELECT 
    f.scheme_name,
    f.category,
    ROUND(p.return_1y, 2) AS return_1y,
    ROUND(p.expense_ratio, 2) AS expense_ratio,
    ROUND(p.return_1y - p.expense_ratio, 2) AS net_return
FROM fact_performance p
JOIN dim_fund f ON p.fund_key = f.fund_key
WHERE p.return_1y IS NOT NULL
ORDER BY net_return DESC;
