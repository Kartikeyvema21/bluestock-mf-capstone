"""
B5 - Automated HTML Email Report (Weekly Performance Summary)
CSS as single line to avoid <br> injection.
"""

import yagmail
import pandas as pd
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
SCORECARD_PATH = BASE_DIR / 'data' / 'processed' / 'fund_scorecard.csv'
SHARPE_PATH = BASE_DIR / 'data' / 'processed' / 'sharpe_ratios.csv'

SENDER_EMAIL = "kartikeyverma676@gmail.com"
SENDER_PASSWORD = "watx glhb kpuz kgea"
SEND_EMAIL = True

def get_recipients():
    print("\n" + "="*50)
    print("Enter recipient email address(es). Separate with commas/spaces.")
    user_input = input("Recipients: ").strip()
    if not user_input:
        return []
    recipients = re.split(r'[ ,;]+', user_input)
    recipients = [r.strip() for r in recipients if r.strip()]
    print(f"✅ Will send to: {', '.join(recipients)}\n")
    return recipients

def generate_html_report():
    scorecard = pd.read_csv(SCORECARD_PATH) if SCORECARD_PATH.exists() else None
    sharpe = pd.read_csv(SHARPE_PATH) if SHARPE_PATH.exists() else None

    if scorecard is not None:
        top10 = scorecard.head(10).copy()
        best_fund = top10.iloc[0]['scheme_name']
        worst_fund = scorecard.iloc[-1]['scheme_name']
        avg_cagr = scorecard['cagr_3y'].mean() * 100
        total_funds = len(scorecard)
        top10_display = top10[['scheme_name', 'total_score', 'overall_rank', 'cagr_3y', 'sharpe_ratio']].copy()
        top10_display['cagr_3y'] = top10_display['cagr_3y'].apply(lambda x: f"{x*100:.2f}%")
        top10_display['sharpe_ratio'] = top10_display['sharpe_ratio'].apply(lambda x: f"{x:.2f}")
        top10_html = top10_display.to_html(index=False, classes='styled-table', escape=False)
    else:
        best_fund = worst_fund = avg_cagr = total_funds = "N/A"
        top10_html = "<p>No scorecard data available.</p>"

    if sharpe is not None:
        top5_sharpe = sharpe.head(5)[['scheme_name', 'sharpe_ratio']].copy()
        top5_sharpe['sharpe_ratio'] = top5_sharpe['sharpe_ratio'].apply(lambda x: f"{x:.2f}")
        sharpe_html = top5_sharpe.to_html(index=False, classes='styled-table', escape=False)
    else:
        sharpe_html = "<p>No Sharpe data available.</p>"

    # Single-line CSS - no newlines inside <style>
    css = ("body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;margin:0;padding:20px;background-color:#eef2f7;color:#1e2a3a;}"
           ".container{max-width:1000px;margin:0 auto;background-color:#ffffff;border-radius:12px;border:1px solid #ccd7e4;overflow-x:auto;}"
           ".header{background-color:#1e3c72;color:white;padding:20px;text-align:center;}"
           ".header h1{margin:0;font-size:28px;}.header p{margin:8px 0 0;font-size:14px;}"
           ".metrics{padding:20px;background-color:#f8fafc;text-align:center;border-bottom:1px solid #e2e8f0;}"
           ".card{display:inline-block;width:200px;background-color:white;border-radius:12px;padding:15px;margin:8px;border:1px solid #cbd5e1;vertical-align:top;box-shadow:0 1px 3px rgba(0,0,0,0.05);}"
           ".card h3{margin:0 0 8px;font-size:15px;color:#2c3e50;}"
           ".card .value{font-size:24px;font-weight:bold;color:#1e3c72;}"
           ".section{padding:20px;border-top:1px solid #e2e8f0;}"
           ".section h2{font-size:20px;margin:0 0 15px;color:#1e3c72;border-left:4px solid #1e3c72;padding-left:12px;}"
           ".styled-table{width:100%;border-collapse:collapse;font-size:14px;background-color:white;margin-top:10px;}"
           ".styled-table th{background-color:#2a5298;color:white;padding:10px;font-weight:bold;text-align:center;border:1px solid #3a6ea5;}"
           ".styled-table td{padding:8px 10px;text-align:center;border:1px solid #dee2e6;}"
           ".styled-table tbody tr:nth-child(even){background-color:#f8f9fc;}"
           ".styled-table tbody tr:nth-child(odd){background-color:#ffffff;}"
           ".footer{background-color:#f1f5f9;text-align:center;padding:15px;font-size:12px;color:#5a6e85;border-top:1px solid #e2e8f0;}"
           ".icon{font-size:18px;margin-right:5px;}"
           "@media (max-width:700px){.card{width:90%;display:block;margin:10px auto;}}")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weekly Mutual Fund Report</title>
<style>{css}</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>✨ Mutual Fund Weekly Pulse ✨</h1>
<p>{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
</div>
<div class="metrics">
<div class="card">
<h3><span class="icon">🏆</span> Star Performer</h3>
<div class="value">{best_fund}</div>
</div>
<div class="card">
<h3><span class="icon">⚠️</span> Needs Review</h3>
<div class="value">{worst_fund}</div>
</div>
<div class="card">
<h3><span class="icon">📈</span> Avg 3Y CAGR</h3>
<div class="value">{avg_cagr:.2f}%</div>
</div>
<div class="card">
<h3><span class="icon">📂</span> Funds Tracked</h3>
<div class="value">{total_funds}</div>
</div>
</div>
<div class="section">
<h2>🏆 Top 10 Funds – Scorecard</h2>
{top10_html}
<p style="margin-top:12px;font-size:12px;color:#5a6e85;">Weights: 30% CAGR(3Y) + 25% Sharpe + 20% Alpha + 15% Expense (inv) + 10% MaxDD (inv)</p>
</div>
<div class="section">
<h2>⚡ Top 5 by Sharpe Ratio</h2>
{sharpe_html}
<p style="margin-top:12px;font-size:12px;color:#5a6e85;">Sharpe = (Fund Return - Risk Free Rate) / Volatility (annualised)</p>
</div>
<div class="footer">
<p>🚀 Powered by Python, Pandas & Plotly | 🔄 ETL pipeline updates daily</p>
<p>📬 Automated weekly report – no reply needed.</p>
</div>
</div>
</body>
</html>"""
    return html

def send_email(recipients, html_content):
    try:
        yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASSWORD)
        subject = f"Weekly Mutual Fund Report – {datetime.now().strftime('%Y-%m-%d')}"
        yag.send(to=recipients, subject=subject, contents=html_content)
        print(f"✅ Email sent to {len(recipients)} recipient(s).")
    except Exception as e:
        print(f"❌ Failed: {e}")

def main():
    print("Verifying data...")
    if not SCORECARD_PATH.exists():
        print(f"Missing: {SCORECARD_PATH}. Run Day 4 notebook first.")
        return
    if not SHARPE_PATH.exists():
        print(f"Warning: {SHARPE_PATH} not found. Continuing without Sharpe.")
    html = generate_html_report()
    if SEND_EMAIL:
        recipients = get_recipients()
        if recipients:
            send_email(recipients, html)
        else:
            print("No recipients.")
    else:
        out = BASE_DIR / 'reports' / 'weekly_report.html'
        out.parent.mkdir(exist_ok=True)
        with open(out, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Saved to {out}")

if __name__ == "__main__":
    main()