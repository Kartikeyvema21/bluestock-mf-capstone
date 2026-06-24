# recommender.py - Mutual Fund Analytics Module
"""
recommender.py – Simple fund recommender based on risk appetite.
Usage:
    python recommender.py [Low|Moderate|High]
Example:
    python recommender.py Moderate
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
NAV_PATH = BASE_DIR / 'data' / 'processed' / 'nav_data_40_funds.csv'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'

def load_and_compute():
    df_nav = pd.read_csv(NAV_PATH, parse_dates=['date'])
    df_nav['daily_return'] = df_nav.groupby('scheme_name')['nav'].pct_change().fillna(0)
    # Compute volatility and Sharpe
    returns = df_nav.groupby('scheme_name')['daily_return']
    volatility = returns.std() * np.sqrt(252)
    sharpe = (returns.mean() - 0.065/252) / returns.std() * np.sqrt(252)
    fund_metrics = pd.DataFrame({'volatility': volatility, 'sharpe_ratio': sharpe}).reset_index()
    # Assign risk grades
    fund_metrics['risk_grade'] = pd.cut(fund_metrics['volatility'],
                                        bins=[0, 0.12, 0.18, 1],
                                        labels=['Low', 'Moderate', 'High'])
    return fund_metrics

def recommend(risk_appetite):
    fund_metrics = load_and_compute()
    filtered = fund_metrics[fund_metrics['risk_grade'] == risk_appetite]
    top3 = filtered.nlargest(3, 'sharpe_ratio')
    return top3[['scheme_name', 'sharpe_ratio', 'volatility']]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        appetite = sys.argv[1]
        if appetite not in ['Low', 'Moderate', 'High']:
            print("Invalid risk appetite. Use: Low, Moderate, or High")
            sys.exit(1)
    else:
        appetite = input("Enter risk appetite (Low / Moderate / High): ").strip().capitalize()
    result = recommend(appetite)
    print(f"\nTop 3 funds for risk appetite '{appetite}':")
    print(result.to_string(index=False))
    # Save to CSV
    output_path = PROCESSED_DIR / f'recommendation_{appetite}.csv'
    result.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")