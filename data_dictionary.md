# Mutual Fund Analytics Platform – Data Dictionary

## Database: bluestock_mf.db (SQLite)
**Last updated:** 2026-06-02

---

## 1. Dimension Tables

### dim_fund
| Column | Type | Description | Source | Example |
|--------|------|-------------|--------|---------|
| `fund_key` | INTEGER PRIMARY KEY | Surrogate key for fund | Auto‑generated | 1 |
| `amfi_code` | INTEGER UNIQUE | AMFI‑assigned scheme code | `nav_history.csv` | 100001 |
| `scheme_name` | TEXT | Full name of the scheme | `nav_history.csv` | HDFC Large Cap Fund |
| `category` | TEXT | Scheme category (Large Cap, Mid Cap, etc.) | `scheme_performance.csv` | Large Cap |
| `fund_house` | TEXT | Asset management company | Derived from scheme_name | HDFC MF |
| `created_date` | DATE | When the record was inserted | System date | 2026-06-02 |

### dim_date
| Column | Type | Description | Source | Example |
|--------|------|-------------|--------|---------|
| `date_key` | INTEGER PRIMARY KEY | Surrogate key in YYYYMMDD format | Derived | 20230102 |
| `full_date` | DATE | Actual calendar date | Derived | 2023-01-02 |
| `year` | INTEGER | Year (e.g., 2023) | Derived | 2023 |
| `quarter` | INTEGER | Quarter of the year (1‑4) | Derived | 1 |
| `month` | INTEGER | Month number (1‑12) | Derived | 1 |
| `month_name` | TEXT | Full month name | Derived | January |
| `day_of_month` | INTEGER | Day of month (1‑31) | Derived | 2 |
| `day_of_week` | INTEGER | Day of week (0=Monday, 6=Sunday) | Derived | 0 |
| `week_of_year` | INTEGER | ISO week number | Derived | 1 |
| `is_weekend` | BOOLEAN | 1 if Saturday or Sunday | Derived | 0 |
| `is_holiday` | BOOLEAN | Reserved for market holidays | Future use | 0 |

---

## 2. Fact Tables

### fact_nav
| Column | Type | Description | Source | Example |
|--------|------|-------------|--------|---------|
| `nav_key` | INTEGER PRIMARY KEY | Surrogate key | Auto‑generated | 1 |
| `fund_key` | INTEGER | Foreign key to `dim_fund` | Lookup | 1 |
| `date_key` | INTEGER | Foreign key to `dim_date` | Lookup | 20230102 |
| `nav` | REAL | Net Asset Value (₹) | `nav_history.csv` | 45.678 |

**Constraints:** `UNIQUE(fund_key, date_key)`

### fact_transactions
| Column | Type | Description | Source | Example |
|--------|------|-------------|--------|---------|
| `transaction_key` | INTEGER PRIMARY KEY | Surrogate key | Auto‑generated | 1 |
| `fund_key` | INTEGER | Foreign key to `dim_fund` | Lookup | 1 |
| `date_key` | INTEGER | Foreign key to `dim_date` | Lookup | 20230102 |
| `transaction_type` | TEXT | SIP / Lumpsum / Redemption | `investor_transactions.csv` | SIP |
| `amount` | REAL | Transaction amount (₹) | `investor_transactions.csv` | 5000 |
| `kyc_status` | TEXT | Verified / Pending / Not Verified | `investor_transactions.csv` | Verified |
| `state` | TEXT | Investor’s state | `investor_transactions.csv` | Maharashtra |
| `city` | TEXT | Investor’s city | `investor_transactions.csv` | Mumbai |

### fact_performance
| Column | Type | Description | Source | Example |
|--------|------|-------------|--------|---------|
| `performance_key` | INTEGER PRIMARY KEY | Surrogate key | Auto‑generated | 1 |
| `fund_key` | INTEGER | Foreign key to `dim_fund` | Lookup | 1 |
| `as_of_date_key` | INTEGER | Snapshot date (usually latest) | Lookup | 20251231 |
| `return_1y` | REAL | 1‑year return (%) | `scheme_performance.csv` | 15.23 |
| `return_3y` | REAL | 3‑year return (%) | `scheme_performance.csv` | 12.45 |
| `return_5y` | REAL | 5‑year return (%) | `scheme_performance.csv` | 10.98 |
| `expense_ratio` | REAL | Expense ratio (% of AUM) | `scheme_performance.csv` | 1.25 |
| `aum_crore` | REAL | Assets under management (₹ crore) | `scheme_performance.csv` | 12345.0 |
| `is_anomaly` | BOOLEAN | Flag if any value is suspicious | Derived | 0 |

### fact_aum
| Column | Type | Description | Source | Example |
|--------|------|-------------|--------|---------|
| `aum_key` | INTEGER PRIMARY KEY | Surrogate key | Auto‑generated | 1 |
| `fund_key` | INTEGER | Foreign key to `dim_fund` | Lookup | 1 |
| `date_key` | INTEGER | Foreign key to `dim_date` | Lookup | 20230102 |
| `aum_crore` | REAL | Estimated AUM (₹ crore) | Derived from NAV | 4567.8 |
| `outstanding_units` | REAL | Number of units outstanding (dummy) | Placeholder | 10000000 |

---

## Validation Rules

| Field | Rule |
|-------|------|
| `nav` | > 0 |
| `amount` | > 0 |
| `expense_ratio` | Between 0.1 and 2.5 (equity funds) |
| `return_1y/3y/5y` | Between -50 and +100 |
| `transaction_type` | One of: SIP, Lumpsum, Redemption |
| `kyc_status` | One of: Verified, Pending, Not Verified |

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-06-02 | Initial version | Capstone Team |
