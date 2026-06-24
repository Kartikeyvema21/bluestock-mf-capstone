import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime

# --------------------------------------------------
# 1. Generate 40 funds NAV data (if you already have df_nav, skip this part)
# --------------------------------------------------
np.random.seed(42)

RISK_FREE_RATE = 0.065
TRADING_DAYS = 252
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2025, 12, 31)

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

# --------------------------------------------------
# 2. Compute daily returns (must be done BEFORE Sharpe)
# --------------------------------------------------
df_nav = df_nav.sort_values(['scheme_name', 'date'])
df_nav['daily_return'] = df_nav.groupby('scheme_name')['nav'].pct_change().fillna(0)
print("Daily returns computed.")

# --------------------------------------------------
# 3. Sharpe Ratio (function works on a Series)
# --------------------------------------------------
def sharpe_ratio(returns_series):
    excess = returns_series - (RISK_FREE_RATE / TRADING_DAYS)
    if excess.std() == 0:
        return 0
    return (excess.mean() / excess.std()) * np.sqrt(TRADING_DAYS)

# Apply to each fund's daily_return Series (result is a Series)
sharpe_series = df_nav.groupby('scheme_name')['daily_return'].apply(sharpe_ratio)

# Convert to DataFrame
sharpe_df = sharpe_series.reset_index()
sharpe_df.columns = ['scheme_name', 'sharpe_ratio']
sharpe_df['category'] = sharpe_df['scheme_name'].map(fund_categories)
sharpe_df['sharpe_rank'] = sharpe_df['sharpe_ratio'].rank(ascending=False).astype(int)
sharpe_df = sharpe_df.sort_values('sharpe_ratio', ascending=False)

# --------------------------------------------------
# 4. Display & Save
# --------------------------------------------------
print("\nTop 10 Funds by Sharpe Ratio:")
print(sharpe_df[['scheme_name', 'sharpe_ratio', 'category', 'sharpe_rank']].head(10).to_string(index=False))

# Directories
os.makedirs('data/processed', exist_ok=True)
os.makedirs('reports/eda_plots', exist_ok=True)

# Plot (using sharpe_df, not Series)
fig = px.bar(sharpe_df.head(20),
             x='scheme_name', y='sharpe_ratio', color='category',
             title='Top 20 Funds by Sharpe Ratio',
             labels={'sharpe_ratio': 'Sharpe Ratio', 'scheme_name': 'Fund Name'})
fig.show()
fig.write_html('reports/eda_plots/sharpe_ratio_top20.html')

# CSV
sharpe_df.to_csv('data/processed/sharpe_ratios.csv', index=False)
print("Sharpe ratios saved to data/processed/sharpe_ratios.csv")