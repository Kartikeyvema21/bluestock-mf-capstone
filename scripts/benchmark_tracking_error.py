import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from datetime import datetime

# ---------- FIX: Load the scorecard that was saved earlier ----------
score = pd.read_csv('data/processed/fund_scorecard.csv')
score['scheme_name'] = score['scheme_name'].astype(str)

# Now the original code can use 'score'
top5 = score['scheme_name'].head(5).tolist()
print("Top 5 funds:", top5)

# Ensure all_dates exists – if not, load or regenerate it
# Assuming you have a 'data/processed/nav_data_40_funds.csv' or regenerate
try:
    df_nav = pd.read_csv('data/processed/nav_data_40_funds.csv', parse_dates=['date'])
    TRADING_DAYS = 252
    all_dates = df_nav['date'].unique()
except:
    # If not found, regenerate (simplified)
    from datetime import datetime, timedelta
    RISK_FREE_RATE = 0.065
    TRADING_DAYS = 252
    START_DATE = datetime(2022, 1, 1)
    END_DATE = datetime(2025, 12, 31)
    all_dates = pd.date_range(START_DATE, END_DATE, freq='D')
    all_dates = all_dates[all_dates.dayofweek < 5]
    # You would also need df_nav; but ideally you already saved it.
    # For simplicity, we raise an error if not found.
    raise FileNotFoundError("Please run complete_performance_analytics.py first to generate required files.")

# Simulate Nifty 50 and Nifty 100 returns for last 3 years
last_3y_dates = all_dates[-3*252:]  # 3 years of trading days

np.random.seed(123)
nifty50_ret = np.random.normal(0.0004, 0.01, len(last_3y_dates))
nifty100_ret = np.random.normal(0.00045, 0.0105, len(last_3y_dates))

df_bench = pd.DataFrame({'date': last_3y_dates, 'Nifty 50': nifty50_ret, 'Nifty 100': nifty100_ret})
for idx in ['Nifty 50', 'Nifty 100']:
    df_bench[f'cum_{idx}'] = (1 + df_bench[idx]).cumprod()

# Create plot
fig = go.Figure()
for idx in ['Nifty 50', 'Nifty 100']:
    fig.add_trace(go.Scatter(x=df_bench['date'], y=df_bench[f'cum_{idx}'], mode='lines',
                             name=idx, line=dict(dash='dash')))

tracking_errors = []
# Load df_nav if not already loaded (need it)
if 'df_nav' not in dir():
    df_nav = pd.read_csv('data/processed/nav_data_40_funds.csv', parse_dates=['date'])
    df_nav['daily_return'] = df_nav.groupby('scheme_name')['nav'].pct_change().fillna(0)

for fund in top5:
    fund_data = df_nav[df_nav['scheme_name'] == fund][['date', 'nav', 'daily_return']].copy()
    merged = pd.merge(fund_data, df_bench, on='date', how='inner')
    if len(merged) > 0:
        merged['cum_return'] = merged['nav'] / merged['nav'].iloc[0]
        fig.add_trace(go.Scatter(x=merged['date'], y=merged['cum_return'], mode='lines', name=fund))
        te = np.std(merged['daily_return'] - nifty50_ret[:len(merged)]) * np.sqrt(TRADING_DAYS)
        tracking_errors.append({'fund': fund, 'tracking_error_vs_Nifty50': te})

fig.update_layout(title='Top 5 Funds vs Benchmark Indices (3 Years)',
                  xaxis_title='Date', yaxis_title='Cumulative Return (Normalized)',
                  legend_title='Fund/Index', height=600)
fig.show()

try:
    fig.write_image('reports/eda_plots/benchmark_comparison.png')
    print("PNG saved.")
except:
    print("Note: 'kaleido' not installed. PNG not saved. Install with: pip install kaleido")
fig.write_html('reports/eda_plots/benchmark_comparison.html')

df_tracking = pd.DataFrame(tracking_errors)
print("\nTracking errors (annualized, vs Nifty 50):")
print(df_tracking)
df_tracking.to_csv('data/processed/tracking_errors.csv', index=False)
print("Benchmark chart and tracking errors saved.")