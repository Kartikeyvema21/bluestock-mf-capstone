import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'db' / 'bluestock_mf.db'
OUTPUT_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# List of tables to export
tables = ['dim_fund', 'dim_date', 'fact_nav', 'fact_transactions', 'fact_performance', 'fact_aum']

for table in tables:
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    output_path = OUTPUT_DIR / f"{table}.csv"
    df.to_csv(output_path, index=False)
    print(f"Exported {table} to {output_path} ({len(df)} rows)")

conn.close()
print("\n✅ All tables exported to CSV.")