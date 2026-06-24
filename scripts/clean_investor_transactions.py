"""
clean_investor_transactions.py
Cleans investor_transactions.csv: standardise transaction types, validate amounts, fix dates, check KYC status.
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Load raw data
trans_df = pd.read_csv(RAW_DIR / 'investor_transactions.csv')
print(f"Raw shape: {trans_df.shape}")

# 1. Standardise transaction_type (convert to title case)
trans_df['transaction_type'] = trans_df['transaction_type'].str.title()
valid_types = ['Sip', 'Lumpsum', 'Redemption']
trans_df = trans_df[trans_df['transaction_type'].isin(valid_types)]

# 2. Validate amount > 0
initial_rows = len(trans_df)
trans_df = trans_df[trans_df['amount'] > 0]
dropped = initial_rows - len(trans_df)
if dropped > 0:
    print(f"Removed {dropped} rows with amount <= 0")

# 3. Fix date format
trans_df['date'] = pd.to_datetime(trans_df['date'], errors='coerce')
trans_df = trans_df.dropna(subset=['date'])

# 4. Validate KYC status
valid_kyc = ['Verified', 'Pending', 'Not Verified']
trans_df = trans_df[trans_df['kyc_status'].isin(valid_kyc)]

# 5. Optional: Remove any rows with missing critical fields
trans_df = trans_df.dropna(subset=['amfi_code', 'transaction_type', 'amount', 'state', 'city'])

# 6. Sort by date for better readability
trans_df = trans_df.sort_values('date')

# Save cleaned CSV
output_path = PROCESSED_DIR / 'investor_transactions_cleaned.csv'
trans_df.to_csv(output_path, index=False)
print(f"Cleaned shape: {trans_df.shape}")
print(f"Saved to {output_path}")
print("\nPreview:")
print(trans_df.head())
print("\nTransaction type distribution:")
print(trans_df['transaction_type'].value_counts())