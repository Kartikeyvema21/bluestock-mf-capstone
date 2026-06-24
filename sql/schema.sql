-- schema.sql - Database schema for Mutual Fund Analytics
-- ============================================
-- Mutual Fund Analytics Platform - Star Schema
-- SQLite version
-- ============================================

-- --------------------------------------------
-- 1. Dimension: fund
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS dim_fund (
    fund_key INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER UNIQUE NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT,
    fund_house TEXT,
    created_date DATE DEFAULT CURRENT_DATE
);

-- --------------------------------------------
-- 2. Dimension: date
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,  -- YYYYMMDD format
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,      -- 1-4
    month INTEGER NOT NULL,        -- 1-12
    month_name TEXT NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,  -- 0=Monday, 6=Sunday
    week_of_year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT 0
);

-- --------------------------------------------
-- 3. Fact: NAV history
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_key INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    nav REAL NOT NULL,
    FOREIGN KEY (fund_key) REFERENCES dim_fund(fund_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    UNIQUE(fund_key, date_key)
);

-- --------------------------------------------
-- 4. Fact: investor transactions
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_key INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,  -- 'SIP', 'Lumpsum', 'Redemption'
    amount REAL NOT NULL,
    kyc_status TEXT,
    state TEXT,
    city TEXT,
    FOREIGN KEY (fund_key) REFERENCES dim_fund(fund_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- --------------------------------------------
-- 5. Fact: scheme performance (point-in-time)
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS fact_performance (
    performance_key INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_key INTEGER NOT NULL,
    as_of_date_key INTEGER NOT NULL,  -- date of this performance snapshot
    return_1y REAL,
    return_3y REAL,
    return_5y REAL,
    expense_ratio REAL,
    aum_crore REAL,
    is_anomaly BOOLEAN DEFAULT 0,
    FOREIGN KEY (fund_key) REFERENCES dim_fund(fund_key),
    FOREIGN KEY (as_of_date_key) REFERENCES dim_date(date_key)
);

-- --------------------------------------------
-- 6. Fact: AUM over time (optional, derived)
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_key INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    aum_crore REAL NOT NULL,
    outstanding_units REAL,  -- optional
    FOREIGN KEY (fund_key) REFERENCES dim_fund(fund_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    UNIQUE(fund_key, date_key)
);

-- --------------------------------------------
-- Create indexes for performance
-- --------------------------------------------
CREATE INDEX idx_nav_fund_date ON fact_nav(fund_key, date_key);
CREATE INDEX idx_transactions_fund_date ON fact_transactions(fund_key, date_key);
CREATE INDEX idx_performance_fund ON fact_performance(fund_key);
CREATE INDEX idx_aum_fund_date ON fact_aum(fund_key, date_key);

