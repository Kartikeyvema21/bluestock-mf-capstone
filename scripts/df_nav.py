"""
df_nav.py – Generate 40 funds daily NAV and daily returns, save to CSV.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

# Parameters
RISK_FREE_RATE = 0.065
TRADING_DAYS = 252
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2025, 12, 31)

# Set seed for reproducibility
np.random.seed(42)

# Trading dates (weekdays only)
all_dates = pd.date_range(START_DATE, END_DATE, freq='D')
all_dates = all_dates[all_dates.dayofweek < 5]

# Create 40 funds
n_funds = 40
fund_names = [f'Fund_{i+1}' for i in range(n_funds)]
categories = ['Large Cap', 'Mid Cap', 'Small Cap', 'Hybrid', 'ELSS']
fund_categories = {name: np.random.choice(categories) for name in fund_names}

# Generate NAV data
nav_data = []
for name in fund_names:
    drift = np.random.uniform(0.08, 0.15) / TRADING_DAYS
    vol = np.random.uniform(0.12, 0.25) / np.sqrt(TRADING_DAYS)
    nav = 100
    for i, d in enumerate(all_dates):
        if i > 0:
            ret = drift + vol * np.random.normal(0, 1)
            nav = nav * (1 + ret)
        nav_data.append([name, d, nav, fund_categories[name]])

df_nav = pd.DataFrame(nav_data, columns=['scheme_name', 'date', 'nav', 'category'])
df_nav['date'] = pd.to_datetime(df_nav['date'])

# Compute daily returns
df_nav = df_nav.sort_values(['scheme_name', 'date'])
df_nav['daily_return'] = df_nav.groupby('scheme_name')['nav'].pct_change().fillna(0)

df_nav = pd.read_csv('data/processed/nav_data_40_funds.csv', parse_dates=['date'])
fund_categories = dict(zip(df_nav['scheme_name'], df_nav['category']))

# Create directories if needed
# Create necessary directories
os.makedirs('data/processed', exist_ok=True)
os.makedirs('reports/eda_plots', exist_ok=True)

# Save to CSV
output_path = 'data/processed/nav_data_40_funds.csv'
df_nav.to_csv(output_path, index=False)
print(f"✅ df_nav saved to {output_path}")
print(f"Shape: {df_nav.shape}")
print(f"Funds: {df_nav['scheme_name'].nunique()}, Dates: {df_nav['date'].nunique()}")
print("\nSample data:")
print(df_nav.head())