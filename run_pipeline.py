"""
run_pipeline.py – Master execution script for Mutual Fund Analytics Platform
Run this script to execute the complete pipeline.
"""

import subprocess
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def check_dependencies():
    """Check if required packages are installed."""
    print("\n" + "="*60)
    print("Checking Dependencies...")
    print("="*60)
    
    required_packages = {
        'pandas': 'pandas',
        'numpy': 'numpy', 
        'sqlalchemy': 'sqlalchemy',
        'plotly': 'plotly',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'scipy': 'scipy',
        'sklearn': 'scikit-learn'
    }
    
    missing = []
    installed = []
    
    for package, install_name in required_packages.items():
        try:
            __import__(package)
            installed.append(package)
            print(f"  ✓ {package}")
        except ImportError:
            missing.append(install_name)
            print(f"  ✗ {package} - MISSING")
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        
        response = input("\nDo you want to install missing packages now? (y/n): ")
        if response.lower() == 'y':
            for package in missing:
                print(f"\nInstalling {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("\n✓ All packages installed!")
            return True
        else:
            return False
    
    print("\n✓ All dependencies satisfied!")
    return True

def run_script(script_path):
    """Run a Python script and handle errors gracefully."""
    if not script_path.exists():
        print(f"⚠ Warning: {script_path.name} not found. Skipping...")
        return False
    
    print(f"\n▶ Running: {script_path.name}")
    print("-" * 40)
    
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, str(script_path)], 
            cwd=BASE_DIR,
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            print(f"✗ Error: {script_path.name} failed with exit code {result.returncode}")
            return False
        
        print(f"✓ Completed: {script_path.name}")
        return True
        
    except Exception as e:
        print(f"✗ Exception: {script_path.name} - {str(e)}")
        return False

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        BASE_DIR / "data" / "raw",
        BASE_DIR / "data" / "processed",
        BASE_DIR / "data" / "db",
        BASE_DIR / "reports" / "eda_plots",
        BASE_DIR / "dashboard",
        BASE_DIR / "logs"
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✓ Directory structure verified")

def run_pipeline():
    """Execute the complete pipeline."""
    print("="*60)
    print("MUTUAL FUND ANALYTICS PLATFORM - MASTER PIPELINE")
    print("="*60)
    
    # Create directories
    print("\n📁 Setting up directory structure...")
    create_directories()
    
    # Check dependencies
    if not check_dependencies():
        print("\n✗ Pipeline aborted. Please install missing dependencies.")
        return False
    
    # List of scripts to run in order
    scripts = [
        ("Data Generation", BASE_DIR / "scripts" / "generate_day2_data.py"),
        ("Clean NAV History", BASE_DIR / "scripts" / "clean_nav_history.py"),
        ("Clean Investor Transactions", BASE_DIR / "scripts" / "clean_investor_transactions.py"),
        ("Clean Scheme Performance", BASE_DIR / "scripts" / "clean_scheme_performance.py"),
        ("Load to SQLite", BASE_DIR / "scripts" / "load_to_sqlite.py"),
        ("Performance Analytics", BASE_DIR / "scripts" / "complete_performance_analytics.py"),
    ]
    
    results = []
    
    for script_name, script_path in scripts:
        print(f"\n{'='*60}")
        print(f"📊 {script_name}")
        print(f"{'='*60}")
        
        success = run_script(script_path)
        results.append((script_name, success))
    
    # Summary
    print("\n" + "="*60)
    print("PIPELINE EXECUTION SUMMARY")
    print("="*60)
    
    successful = sum(1 for _, success in results if success)
    failed = len(results) - successful
    
    for script_name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {script_name}")
    
    print(f"\nTotal: {successful} successful, {failed} failed")
    
    if failed == 0:
        print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("\n📊 Next Steps:")
        print("  1. Open Power BI dashboard: dashboard/bluestock_mf_dashboard.pbix")
        print("  2. Explore Jupyter notebooks: notebooks/")
        print("  3. Check generated reports: reports/")
        print("  4. View live dashboard: https://app.powerbi.com/...")
        return True
    else:
        print("\n⚠ Pipeline completed with errors.")
        print("   Check the error messages above and fix issues.")
        return False

def main():
    """Main entry point."""
    try:
        success = run_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()