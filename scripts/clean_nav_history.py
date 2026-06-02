"""
clean_nav_history.py
Cleans nav_history.csv: parse dates, sort, forward-fill missing NAV, remove duplicates, validate NAV > 0.
"""

import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Load raw data
nav_df = pd.read_csv(RAW_DIR / 'nav_history.csv')
print(f"Raw shape: {nav_df.shape}")

# 1. Parse date column
nav_df['date'] = pd.to_datetime(nav_df['date'])

# 2. Sort by amfi_code and date
nav_df = nav_df.sort_values(['amfi_code', 'date'])

# 3. Forward-fill missing NAV for weekends/holidays
# Create a full date range for all schemes
all_dates = pd.date_range(start=nav_df['date'].min(), end=nav_df['date'].max(), freq='D')
full_dfs = []

for code in nav_df['amfi_code'].unique():
    scheme_df = nav_df[nav_df['amfi_code'] == code].copy()
    # Reindex to all dates
    scheme_df = scheme_df.set_index('date').reindex(all_dates)
    scheme_df['amfi_code'] = code
    scheme_df['scheme_name'] = scheme_df['scheme_name'].ffill()
    scheme_df['nav'] = scheme_df['nav'].ffill()
    scheme_df = scheme_df.reset_index().rename(columns={'index': 'date'})
    full_dfs.append(scheme_df)

nav_clean = pd.concat(full_dfs, ignore_index=True)

# 4. Remove duplicates (keep last per scheme+date if any)
nav_clean = nav_clean.drop_duplicates(subset=['amfi_code', 'date'], keep='last')

# 5. Validate NAV > 0
initial_rows = len(nav_clean)
nav_clean = nav_clean[nav_clean['nav'] > 0]
dropped = initial_rows - len(nav_clean)
if dropped > 0:
    print(f"Removed {dropped} rows with NAV <= 0")

# Save cleaned CSV
output_path = PROCESSED_DIR / 'nav_history_cleaned.csv'
nav_clean.to_csv(output_path, index=False)
print(f"Cleaned shape: {nav_clean.shape}")
print(f"Saved to {output_path}")
print("\nPreview:")
print(nav_clean.head())