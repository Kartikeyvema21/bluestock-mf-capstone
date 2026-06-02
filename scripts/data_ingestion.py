"""
data_ingestion.py
Mutual Fund Analytics Platform - Data Ingestion Module

Reads raw mutual fund CSV files from data/raw/, standardises them,
handles missing values, and saves processed data to data/processed/.
"""

import pandas as pd
import numpy as np
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / 'data' / 'raw'
PROCESSED_DATA_DIR = BASE_DIR / 'data' / 'processed'

# Ensure processed directory exists
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

def find_csv_files():
    """Find all CSV files in raw data directory."""
    return list(RAW_DATA_DIR.glob('*.csv'))

def standardise_columns(df):
    """Standardise column names to lowercase, replace spaces with underscores."""
    df.columns = (
        df.columns.str.lower()
        .str.strip()
        .str.replace(' ', '_')
        .str.replace(r'[^\w_]', '', regex=True)
    )
    return df

def validate_mutual_fund_data(df):
    """
    Perform basic validation on mutual fund data.
    Expected columns: scheme_code, scheme_name, nav, date, fund_house
    """
    required_cols = ['scheme_code', 'scheme_name', 'nav', 'date']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    # Convert NAV to numeric
    df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
    
    # Drop rows where date or nav is null after conversion
    initial_rows = len(df)
    df = df.dropna(subset=['date', 'nav'])
    dropped_rows = initial_rows - len(df)
    if dropped_rows > 0:
        logger.warning(f"Dropped {dropped_rows} rows due to invalid date or NAV.")
    
    # Ensure scheme_code is string
    df['scheme_code'] = df['scheme_code'].astype(str)
    return df

def ingest_raw_data():
    """Main ingestion function: reads, cleans, and saves processed data."""
    csv_files = find_csv_files()
    if not csv_files:
        logger.error(f"No CSV files found in {RAW_DATA_DIR}")
        return
    
    logger.info(f"Found {len(csv_files)} CSV files: {[f.name for f in csv_files]}")
    
    all_dfs = []
    for file_path in csv_files:
        logger.info(f"Processing {file_path.name}...")
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            df = standardise_columns(df)
            df = validate_mutual_fund_data(df)
            all_dfs.append(df)
        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")
    
    if not all_dfs:
        logger.error("No valid dataframes to concatenate.")
        return
    
    # Combine all dataframes
    combined_df = pd.concat(all_dfs, ignore_index=True)
    logger.info(f"Combined dataframe shape: {combined_df.shape}")
    
    # Sort by date for each scheme (optional)
    combined_df = combined_df.sort_values(['scheme_code', 'date'])
    
    # Save to processed folder
    output_path = PROCESSED_DATA_DIR / 'mutual_funds_processed.csv'
    combined_df.to_csv(output_path, index=False)
    logger.info(f"Saved processed data to {output_path}")
    
    return combined_df

if __name__ == "__main__":
    df = ingest_raw_data()
    if df is not None:
        print("\n📊 Processed data preview:")
        print(df.head())
        print(f"\n✅ Total rows: {len(df)}")