"""
generate_day2_data.py
Creates three CSV files required for Day 2:
- nav_history.csv
- investor_transactions.csv
- scheme_performance.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
RAW_DIR.mkdir(parents=True, exist_ok=True)

np.random.seed(42)

# ----- 1. NAV HISTORY -----
amfi_codes = [100001, 100002, 100003, 100004, 100005]
fund_names = [
    "HDFC Large Cap Fund", "SBI Bluechip Fund", "ICICI Balanced Advantage",
    "Axis Small Cap Fund", "Kotak Equity Opportunities"
]
start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 12, 31)
date_range = pd.date_range(start=start_date, end=end_date, freq='D')
date_range = date_range[date_range.dayofweek < 5]  # weekdays only

nav_records = []
for code, name in zip(amfi_codes, fund_names):
    base_nav = np.random.uniform(20, 150)
    for i, dt in enumerate(date_range):
        change = np.random.normal(0.0005, 0.015)
        if i == 0:
            nav = base_nav
        else:
            nav = nav_records[-1][2] * (1 + change)
        nav = max(nav, 0.1)
        nav_records.append([code, name, round(nav, 3), dt.strftime('%Y-%m-%d')])

nav_df = pd.DataFrame(nav_records, columns=['amfi_code', 'scheme_name', 'nav', 'date'])
nav_df.to_csv(RAW_DIR / 'nav_history.csv', index=False)
print(f"Created nav_history.csv with {len(nav_df)} rows")

# ----- 2. INVESTOR TRANSACTIONS -----
states = ['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Gujarat', 'West Bengal']
cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Ahmedabad', 'Kolkata']
kyc_status = ['Verified', 'Pending', 'Not Verified']
transaction_types = ['SIP', 'Lumpsum', 'Redemption']
sip_amounts = [500, 1000, 2000, 5000, 10000]
lumpsum_amounts = [5000, 10000, 25000, 50000, 100000]
redemption_amounts = [1000, 5000, 10000, 25000]

n_trans = 5000
trans_dates = pd.date_range(start='2023-01-01', end='2025-12-31', freq='D')
trans_data = []
for _ in range(n_trans):
    trans_type = np.random.choice(transaction_types, p=[0.6, 0.3, 0.1])
    if trans_type == 'SIP':
        amount = np.random.choice(sip_amounts)
    elif trans_type == 'Lumpsum':
        amount = np.random.choice(lumpsum_amounts)
    else:
        amount = np.random.choice(redemption_amounts)
    
    # Safely get a random date and convert to datetime
    random_idx = np.random.randint(0, len(trans_dates))
    random_date = trans_dates[random_idx]
    # Convert to Python datetime
    if hasattr(random_date, 'to_pydatetime'):
        date_obj = random_date.to_pydatetime()
    else:
        date_obj = random_date
    
    trans_data.append([
        np.random.choice(amfi_codes),
        np.random.choice(kyc_status),
        trans_type,
        amount,
        np.random.choice(states),
        np.random.choice(cities),
        date_obj.strftime('%Y-%m-%d')
    ])

trans_df = pd.DataFrame(trans_data, columns=[
    'amfi_code', 'kyc_status', 'transaction_type', 'amount', 'state', 'city', 'date'
])
trans_df.to_csv(RAW_DIR / 'investor_transactions.csv', index=False)
print(f"Created investor_transactions.csv with {len(trans_df)} rows")

# ----- 3. SCHEME PERFORMANCE -----
perf_records = []
for code, name in zip(amfi_codes, fund_names):
    perf_records.append([
        code, name,
        round(np.random.uniform(8, 25), 2),
        round(np.random.uniform(10, 18), 2),
        round(np.random.uniform(8, 15), 2),
        round(np.random.uniform(0.5, 2.3), 2),
        np.random.choice(['Large Cap', 'Mid Cap', 'Small Cap', 'Hybrid']),
        round(np.random.uniform(100, 50000), 0)
    ])
perf_df = pd.DataFrame(perf_records, columns=[
    'amfi_code', 'scheme_name', 'return_1y', 'return_3y', 'return_5y',
    'expense_ratio', 'category', 'aum_crore'
])
perf_df.to_csv(RAW_DIR / 'scheme_performance.csv', index=False)
print(f"Created scheme_performance.csv with {len(perf_df)} rows")

print("\n✅ All three CSV files generated in data/raw/")