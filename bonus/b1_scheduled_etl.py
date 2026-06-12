# bonus/b1_scheduled_etl.py
import requests
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'db' / 'bluestock_mf.db'

def fetch_nav_for_scheme(scheme_code):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data['data']  # list of {date, nav}
    return []

def update_database():
    conn = sqlite3.connect(DB_PATH)
    schemes = pd.read_sql("SELECT fund_key, amfi_code FROM dim_fund", conn)
    for _, row in schemes.iterrows():
        nav_data = fetch_nav_for_scheme(row['amfi_code'])
        if nav_data:
            latest = nav_data[-1]
            nav_date = datetime.strptime(latest['date'], '%d-%m-%Y').date()
            nav_value = float(latest['nav'])
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO fact_nav (fund_key, date_key, nav)
                VALUES (?, (SELECT date_key FROM dim_date WHERE full_date = ?), ?)
            """, (row['fund_key'], nav_date, nav_value))
    conn.commit()
    conn.close()
    print(f"Updated NAV at {datetime.now()}")

if __name__ == "__main__":
    update_database()