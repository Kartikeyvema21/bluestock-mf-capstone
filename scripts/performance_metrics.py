"""
performance_metrics.py
Calculates CAGR, annualised returns, volatility, Sharpe ratio, Beta, Max Drawdown, VaR.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'db' / 'bluestock_mf.db'
OUTPUT_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RISK_FREE_RATE = 0.06  # 6% assumed
TRADING_DAYS = 252

conn = sqlite3.connect(DB_PATH)

# Load NAV data with fund info
nav_df = pd.read_sql("""
    SELECT f.scheme_name, f.amfi_code, n.date_key, n.nav, d.full_date
    FROM fact_nav n
    JOIN dim_fund f ON n.fund_key = f.fund_key
    JOIN dim_date d ON n.date_key = d.date_key
    ORDER BY f.scheme_name, d.full_date
""", conn)

nav_df['full_date'] = pd.to_datetime(nav_df['full_date'])
nav_df['daily_return'] = nav_df.groupby('scheme_name')['nav'].pct_change()

# Simulated market returns (for Beta)
np.random.seed(42)
market_df = nav_df[['full_date']].drop_duplicates().sort_values('full_date')
market_df['market_return'] = np.random.normal(0.0008, 0.012, len(market_df))

results = []

for name, group in nav_df.groupby('scheme_name'):
    group = group.sort_values('full_date').dropna(subset=['daily_return'])
    if len(group) < 2:
        continue

    # CAGR
    start_nav = group['nav'].iloc[0]
    end_nav = group['nav'].iloc[-1]
    years = (group['full_date'].iloc[-1] - group['full_date'].iloc[0]).days / 365.25
    cagr = (end_nav / start_nav) ** (1 / years) - 1 if years > 0 else np.nan

    # Annualised Return
    total_return = group['daily_return'].add(1).prod() - 1
    days = len(group)
    annual_return = (1 + total_return) ** (TRADING_DAYS / days) - 1

    # Annualised Volatility
    daily_vol = group['daily_return'].std()
    annual_vol = daily_vol * np.sqrt(TRADING_DAYS)

    # Sharpe Ratio
    sharpe = (annual_return - RISK_FREE_RATE) / annual_vol if annual_vol != 0 else np.nan

    # Beta
    fund_returns = group.set_index('full_date')['daily_return']
    market_returns = market_df.set_index('full_date')['market_return']
    aligned = pd.merge(fund_returns, market_returns, left_index=True, right_index=True, how='inner')
    if len(aligned) > 1:
        cov = np.cov(aligned['daily_return'], aligned['market_return'])[0,1]
        var_market = np.var(aligned['market_return'])
        beta = cov / var_market if var_market != 0 else np.nan
    else:
        beta = np.nan

    # Max Drawdown
    cumulative = (1 + group['daily_return']).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()

    # Historical VaR (95%)
    var_95 = group['daily_return'].quantile(0.05)

    results.append({
        'scheme_name': name,
        'cagr': cagr,
        'annualised_return': annual_return,
        'annualised_volatility': annual_vol,
        'sharpe_ratio': sharpe,
        'beta': beta,
        'max_drawdown': max_drawdown,
        'var_95': var_95,
        'start_date': group['full_date'].iloc[0],
        'end_date': group['full_date'].iloc[-1],
        'n_days': days
    })

results_df = pd.DataFrame(results)

# Format percentages
for col in ['cagr', 'annualised_return', 'annualised_volatility', 'max_drawdown', 'var_95']:
    results_df[col] = results_df[col].apply(lambda x: f"{x*100:.2f}%" if pd.notnull(x) else "N/A")

results_df['sharpe_ratio'] = results_df['sharpe_ratio'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
results_df['beta'] = results_df['beta'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")

output_path = OUTPUT_DIR / 'fund_performance_metrics.csv'
results_df.to_csv(output_path, index=False)
print(f"Performance metrics saved to {output_path}")
print("\n=== Fund Performance Summary ===")
print(results_df.to_string(index=False))

conn.close()
