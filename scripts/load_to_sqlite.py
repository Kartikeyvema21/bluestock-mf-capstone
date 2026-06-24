"""
load_to_sqlite.py – recreate schema from schema.sql, then load cleaned data.
"""

import pandas as pd
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
DB_PATH = BASE_DIR / 'data' / 'db' / 'bluestock_mf.db'
SCHEMA_PATH = BASE_DIR / 'sql' / 'schema.sql'

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("Resetting database using schema.sql")
print("=" * 60)

# 1. Drop all existing tables (to start fresh)
cursor.executescript("""
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;
""")
print("✅ Dropped existing tables")

# 2. Create fresh tables from schema.sql
with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    schema_sql = f.read()
cursor.executescript(schema_sql)
print("✅ Recreated tables from schema.sql")

# 3. Load data into dim_fund
nav_df = pd.read_csv(PROCESSED_DIR / 'nav_history_cleaned.csv')
unique_funds = nav_df[['amfi_code', 'scheme_name']].drop_duplicates()
perf_df = pd.read_csv(PROCESSED_DIR / 'scheme_performance_cleaned.csv')
fund_metadata = perf_df[['amfi_code', 'category']].drop_duplicates()
unique_funds = unique_funds.merge(fund_metadata, on='amfi_code', how='left')
unique_funds['fund_house'] = unique_funds['scheme_name'].apply(lambda x: x.split()[0] + ' MF')
unique_funds.to_sql('dim_fund', conn, if_exists='append', index=False)
print(f"✅ dim_fund: {len(unique_funds)} rows")

# 4. Load dim_date
def create_date_dimension(date_series):
    dates = pd.to_datetime(date_series.unique())
    dim_data = []
    for d in dates:
        dim_data.append({
            'date_key': int(d.strftime('%Y%m%d')),
            'full_date': d.strftime('%Y-%m-%d'),
            'year': d.year,
            'quarter': (d.month - 1) // 3 + 1,
            'month': d.month,
            'month_name': d.strftime('%B'),
            'day_of_month': d.day,
            'day_of_week': d.weekday(),
            'week_of_year': d.isocalendar()[1],
            'is_weekend': 1 if d.weekday() >= 5 else 0,
            'is_holiday': 0
        })
    return pd.DataFrame(dim_data)

nav_dates = pd.to_datetime(nav_df['date'])
trans_dates = pd.to_datetime(pd.read_csv(PROCESSED_DIR / 'investor_transactions_cleaned.csv')['date'])
perf_dates = pd.to_datetime('2025-12-31')
all_dates = pd.concat([nav_dates, trans_dates, pd.Series([perf_dates])]).drop_duplicates()
dim_date_df = create_date_dimension(all_dates)
dim_date_df.to_sql('dim_date', conn, if_exists='append', index=False)
print(f"✅ dim_date: {len(dim_date_df)} rows")

# 5. Create surrogate key maps
fund_key_map = pd.read_sql("SELECT fund_key, amfi_code FROM dim_fund", conn)
fund_key_map = dict(zip(fund_key_map['amfi_code'], fund_key_map['fund_key']))

date_key_map = pd.read_sql("SELECT date_key, full_date FROM dim_date", conn)
date_key_map = dict(zip(date_key_map['full_date'], date_key_map['date_key']))

# 6. fact_nav
fact_nav = nav_df[['amfi_code', 'date', 'nav']].copy()
fact_nav['fund_key'] = fact_nav['amfi_code'].map(fund_key_map)
fact_nav['date_key'] = pd.to_datetime(fact_nav['date']).dt.strftime('%Y-%m-%d').map(date_key_map)
fact_nav = fact_nav.dropna(subset=['fund_key', 'date_key'])
fact_nav = fact_nav[['fund_key', 'date_key', 'nav']].drop_duplicates()
fact_nav.to_sql('fact_nav', conn, if_exists='append', index=False)
print(f"✅ fact_nav: {len(fact_nav)} rows")

# 7. fact_transactions
trans_df = pd.read_csv(PROCESSED_DIR / 'investor_transactions_cleaned.csv')
fact_trans = trans_df[['amfi_code', 'date', 'transaction_type', 'amount', 'kyc_status', 'state', 'city']].copy()
fact_trans['fund_key'] = fact_trans['amfi_code'].map(fund_key_map)
fact_trans['date_key'] = pd.to_datetime(fact_trans['date']).dt.strftime('%Y-%m-%d').map(date_key_map)
fact_trans = fact_trans.dropna(subset=['fund_key', 'date_key'])
fact_trans = fact_trans[['fund_key', 'date_key', 'transaction_type', 'amount', 'kyc_status', 'state', 'city']]
fact_trans.to_sql('fact_transactions', conn, if_exists='append', index=False)
print(f"✅ fact_transactions: {len(fact_trans)} rows")

# 8. fact_performance
perf_clean = pd.read_csv(PROCESSED_DIR / 'scheme_performance_cleaned.csv')
fact_perf = perf_clean[['amfi_code', 'return_1y', 'return_3y', 'return_5y', 'expense_ratio', 'aum_crore', 'is_anomaly']].copy()
fact_perf['fund_key'] = fact_perf['amfi_code'].map(fund_key_map)
as_of_date = dim_date_df['full_date'].max()
fact_perf['as_of_date_key'] = date_key_map[as_of_date]
fact_perf = fact_perf.dropna(subset=['fund_key'])
fact_perf = fact_perf[['fund_key', 'as_of_date_key', 'return_1y', 'return_3y', 'return_5y', 'expense_ratio', 'aum_crore', 'is_anomaly']]
fact_perf.to_sql('fact_performance', conn, if_exists='append', index=False)
print(f"✅ fact_performance: {len(fact_perf)} rows")

# 9. fact_aum (derived)
fact_aum = fact_nav.copy()
fact_aum['aum_crore'] = fact_aum['nav'] * 10
fact_aum['outstanding_units'] = 1e7
fact_aum = fact_aum[['fund_key', 'date_key', 'aum_crore', 'outstanding_units']]
fact_aum.to_sql('fact_aum', conn, if_exists='append', index=False)
print(f"✅ fact_aum: {len(fact_aum)} rows")

# Verify
print("\n" + "=" * 60)
print("VERIFICATION – Row counts:")
for table in ['dim_fund', 'dim_date', 'fact_nav', 'fact_transactions', 'fact_performance', 'fact_aum']:
    cnt = pd.read_sql(f"SELECT COUNT(*) FROM {table}", conn).iloc[0, 0]
    print(f"{table:20} : {cnt:>8,} rows")

conn.close()
print("\n✅ Database loaded successfully with schema.sql")