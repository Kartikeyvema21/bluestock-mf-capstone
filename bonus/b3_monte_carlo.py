# bonus/b3_monte_carlo.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DF_NAV_PATH = BASE_DIR / 'data' / 'processed' / 'nav_data_40_funds.csv'

def run_monte_carlo(fund_name, n_sims=10000, years=5):
    df_nav = pd.read_csv(DF_NAV_PATH, parse_dates=['date'])
    fund_nav = df_nav[df_nav['scheme_name'] == fund_name]['nav']
    returns = fund_nav.pct_change().dropna()
    mu = returns.mean()
    sigma = returns.std()
    last_nav = fund_nav.iloc[-1]
    days = years * 252
    dt = 1/252
    
    sims = np.zeros((days, n_sims))
    sims[0] = last_nav
    for t in range(1, days):
        z = np.random.normal(0, 1, n_sims)
        drift = (mu - 0.5 * sigma**2) * dt
        shock = sigma * np.sqrt(dt) * z
        sims[t] = sims[t-1] * np.exp(drift + shock)
    
    percentiles = np.percentile(sims, [5, 50, 95], axis=1)
    dates = pd.date_range(start=df_nav['date'].max(), periods=days, freq='B')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=percentiles[1], mode='lines', name='Median'))
    fig.add_trace(go.Scatter(x=dates, y=percentiles[0], fill=None, mode='lines', name='5th %'))
    fig.add_trace(go.Scatter(x=dates, y=percentiles[2], fill='tonexty', mode='lines', name='95th %'))
    fig.update_layout(title=f'Monte Carlo NAV Projection – {fund_name} (5 years)',
                      xaxis_title='Date', yaxis_title='NAV (₹)')
    fig.show()
    fig.write_html(BASE_DIR / 'reports' / 'eda_plots' / f'monte_carlo_{fund_name}.html')

if __name__ == "__main__":
    run_monte_carlo(fund_name="Fund_1")  # change fund name as needed