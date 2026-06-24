"""
clean_scheme_performance.py
Cleans scheme_performance.csv: validate numeric returns, expense ratio range, flag anomalies.
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Load raw data
perf_df = pd.read_csv(RAW_DIR / 'scheme_performance.csv')
print(f"Raw shape: {perf_df.shape}")

# 1. Ensure return columns are numeric
return_cols = ['return_1y', 'return_3y', 'return_5y']
for col in return_cols:
    perf_df[col] = pd.to_numeric(perf_df[col], errors='coerce')

# 2. Ensure expense_ratio is numeric
perf_df['expense_ratio'] = pd.to_numeric(perf_df['expense_ratio'], errors='coerce')

# 3. Flag anomalies
perf_df['is_anomaly'] = False

# Expense ratio range (0.1% to 2.5% for equity funds)
expense_valid = (perf_df['expense_ratio'] >= 0.1) & (perf_df['expense_ratio'] <= 2.5)
perf_df.loc[~expense_valid, 'is_anomaly'] = True

# Return values should be between -50% and +100%
for col in return_cols:
    ret_valid = (perf_df[col] >= -50) & (perf_df[col] <= 100)
    perf_df.loc[~ret_valid, 'is_anomaly'] = True

# 4. Drop rows where all returns are NaN
perf_df = perf_df.dropna(subset=return_cols, how='all')

# 5. Fill missing expense ratios with median
perf_df['expense_ratio'] = perf_df['expense_ratio'].fillna(perf_df['expense_ratio'].median())

# 6. Save cleaned data
output_path = PROCESSED_DIR / 'scheme_performance_cleaned.csv'
perf_df.to_csv(output_path, index=False)

print(f"Cleaned shape: {perf_df.shape}")
print(f"Anomalies flagged: {perf_df['is_anomaly'].sum()}")
print(f"Saved to {output_path}")