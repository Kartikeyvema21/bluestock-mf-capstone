# bonus/b4_markowitz.py
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCORECARD_PATH = BASE_DIR / 'data' / 'processed' / 'fund_scorecard.csv'
DF_NAV_PATH = BASE_DIR / 'data' / 'processed' / 'nav_data_40_funds.csv'

def portfolio_performance(weights, mean_returns, cov_matrix):
    """Calculate annualised return and risk (standard deviation)."""
    ret = np.sum(mean_returns * weights) * 252
    risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return ret, risk

def negative_sharpe(weights, mean_returns, cov_matrix, risk_free=0.065):
    """Negative Sharpe ratio for minimisation."""
    ret, risk = portfolio_performance(weights, mean_returns, cov_matrix)
    if risk == 0:
        return 0
    return -(ret - risk_free) / risk

def run_markowitz(selected_funds):
    """Compute optimal weights to maximise Sharpe ratio."""
    df_nav = pd.read_csv(DF_NAV_PATH, parse_dates=['date'])
    # Ensure daily_return exists; if not, compute it
    if 'daily_return' not in df_nav.columns:
        df_nav = df_nav.sort_values(['scheme_name', 'date'])
        df_nav['daily_return'] = df_nav.groupby('scheme_name')['nav'].pct_change().fillna(0)
    
    # Pivot to get returns matrix
    returns_df = df_nav[df_nav['scheme_name'].isin(selected_funds)].pivot(
        index='date', columns='scheme_name', values='daily_return')
    mean_returns = returns_df.mean()
    cov_matrix = returns_df.cov()
    
    n = len(selected_funds)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(n))
    initial_weights = n * [1./n]
    
    result = minimize(negative_sharpe, initial_weights, args=(mean_returns, cov_matrix, 0.065),
                      method='SLSQP', bounds=bounds, constraints=constraints)
    if result.success:
        return result.x
    else:
        print("Optimisation failed:", result.message)
        return initial_weights

if __name__ == "__main__":
    # Check if required files exist
    if not SCORECARD_PATH.exists():
        print(f"Error: {SCORECARD_PATH} not found. Run Day 4 notebook first.")
        exit(1)
    if not DF_NAV_PATH.exists():
        print(f"Error: {DF_NAV_PATH} not found. Run Day 4 notebook first.")
        exit(1)
    
    # Load top 5 funds from scorecard
    score = pd.read_csv(SCORECARD_PATH)
    top5 = score['scheme_name'].head(5).tolist()
    print("Selected funds (top 5 by scorecard):")
    for i, f in enumerate(top5, 1):
        print(f"  {i}. {f}")
    
    # Compute optimal weights
    weights = run_markowitz(top5)
    
    print("\nOptimal portfolio weights (maximising Sharpe ratio):")
    for name, w in zip(top5, weights):
        print(f"  {name}: {w:.2%}")
    
    # Save weights to CSV (optional)
    output_path = BASE_DIR / 'data' / 'processed' / 'markowitz_weights.csv'
    pd.DataFrame({'fund': top5, 'weight': weights}).to_csv(output_path, index=False)
    print(f"\nWeights saved to {output_path}")