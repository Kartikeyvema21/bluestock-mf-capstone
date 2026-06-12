"""
run_pipeline.py – Master execution script for Mutual Fund Analytics Platform
Run this script to execute the complete pipeline.
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def run_script(script_path):
    print(f"\n>>> Running {script_path}...")
    result = subprocess.run([sys.executable, str(script_path)], cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"Error running {script_path}")
        sys.exit(1)
    print(f"Completed {script_path}")

if __name__ == "__main__":
    print("="*60)
    print("Mutual Fund Analytics Platform – Master Pipeline")
    print("="*60)

    # Day 1 & 2: Data generation and cleaning
    run_script(BASE_DIR / "scripts" / "generate_day2_data.py")
    run_script(BASE_DIR / "scripts" / "clean_nav_history.py")
    run_script(BASE_DIR / "scripts" / "clean_investor_transactions.py")
    run_script(BASE_DIR / "scripts" / "clean_scheme_performance.py")
    run_script(BASE_DIR / "scripts" / "load_to_sqlite.py")

    # Day 4: Performance metrics
    run_script(BASE_DIR / "scripts" / "complete_performance_analytics.py")

    # Day 6: Advanced analytics (notebook can also be converted to script)
    print("\n>>> Run advanced analytics notebook manually or convert to script.")

    print("\n✅ Pipeline completed successfully.")