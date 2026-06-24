"""
generate_sample_data.py
Creates realistic sample mutual fund NAV CSV files in data/raw/
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Seed for reproducibility
np.random.seed(42)

# Fund details: (scheme_code, scheme_name, fund_house, base_nav)
funds = [
    ("MF101", "HDFC Large Cap Fund", "HDFC Mutual Fund", 45.0),
    ("MF102", "SBI Bluechip Fund", "SBI Mutual Fund", 78.5),
    ("MF103", "ICICI Balanced Advantage Fund", "ICICI Prudential", 32.0),
    ("MF104", "Axis Small Cap Fund", "Axis Mutual Fund", 22.3),
    ("MF105", "Kotak Equity Opportunities", "Kotak Mahindra", 55.8),
]

def generate_nav_series(base_nav, days, volatility=0.015, drift=0.0002):
    """Generate random walk NAV series."""
    returns = np.random.normal(drift, volatility, days)
    nav = base_nav * np.exp(np.cumsum(returns))
    return nav

def create_fund_csv(fund_info, start_date, end_date):
    scheme_code, scheme_name, fund_house, base_nav = fund_info
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    # Remove weekends for realism
    date_range = date_range[date_range.dayofweek < 5]
    days = len(date_range)
    nav_values = generate_nav_series(base_nav, days)
    
    df = pd.DataFrame({
        'scheme_code': scheme_code,
        'scheme_name': scheme_name,
        'fund_house': fund_house,
        'date': date_range,
        'nav': np.round(nav_values, 3)
    })
    return df

# Date range: last 2 years
end = datetime(2025, 12, 31)
start = end - timedelta(days=2*365)

# Generate one CSV per fund
for fund in funds:
    df = create_fund_csv(fund, start, end)
    filename = f"{fund[0]}_{fund[1].replace(' ', '_')}.csv"
    filepath = RAW_DIR / filename
    df.to_csv(filepath, index=False)
    print(f"Created: {filepath} ({len(df)} rows)")

print("\n✅ Sample data generation complete. Now run data_ingestion.py")