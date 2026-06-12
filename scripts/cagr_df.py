import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# ============================================
# 1. Generate 40 funds NAV data (2022–2025)
# ============================================
np.random.seed(42)

RISK_FREE_RATE = 0.065
TRADING_DAYS = 252
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2025, 12, 31)

# Trading dates (weekdays only)
all_dates = pd.date_range(START_DATE, END_DATE, freq='D')
all_dates = all_dates[all_dates.dayofweek < 5]

n_funds = 40
fund_names = [f'Fund_{i+1}' for i in range(n_funds)]
categories = ['Large Cap', 'Mid Cap', 'Small Cap', 'Hybrid', 'ELSS']
fund_categories = {name: np.random.choice(categories) for name in fund_names}

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
print(f"Generated {df_nav['scheme_name'].nunique()} funds, {len(df_nav)} NAV records")

# ============================================
# 2. Compute daily returns (optional, but good to have)
# ============================================
df_nav = df_nav.sort_values(['scheme_name', 'date'])
df_nav['daily_return'] = df_nav.groupby('scheme_name')['nav'].pct_change().fillna(0)

# ============================================
# 3. CAGR calculation
# ============================================
def calc_cagr(group):
    group = group.sort_values('date')
    end_nav = group['nav'].iloc[-1]
    end_date = group['date'].iloc[-1]
    
    def get_nav_ago(days):
        target = end_date - timedelta(days=days)
        sub = group[group['date'] >= target]
        return sub['nav'].iloc[0] if len(sub) > 0 else np.nan
    
    nav_1y = get_nav_ago(365)
    nav_3y = get_nav_ago(3*365)
    nav_5y = get_nav_ago(5*365)
    
    cagr_1y = (end_nav / nav_1y) - 1 if not np.isnan(nav_1y) else np.nan
    cagr_3y = (end_nav / nav_3y)**(1/3) - 1 if not np.isnan(nav_3y) else np.nan
    cagr_5y = (end_nav / nav_5y)**(1/5) - 1 if not np.isnan(nav_5y) else np.nan
    return pd.Series({'cagr_1y': cagr_1y, 'cagr_3y': cagr_3y, 'cagr_5y': cagr_5y})

cagr_df = df_nav.groupby('scheme_name').apply(calc_cagr).reset_index()
cagr_df['category'] = cagr_df['scheme_name'].map(fund_categories)
print("\nCAGR results (first 10):")
print(cagr_df.head(10))

# ============================================
# 4. Save to CSV
# ============================================
os.makedirs('data/processed', exist_ok=True)
cagr_df.to_csv('data/processed/cagr_results.csv', index=False)
print("Saved to data/processed/cagr_results.csv")