import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
import os

# ============================================
# 1. Generate 40 funds NAV data (2022–2025)
# ============================================
np.random.seed(42)

RISK_FREE_RATE = 0.065
TRADING_DAYS = 252
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2025, 12, 31)

all_dates = pd.date_range(START_DATE, END_DATE, freq='D')
all_dates = all_dates[all_dates.dayofweek < 5]

n_funds = 40
fund_names = [f'Fund_{i+1}' for i in range(n_funds)]
categories = ['Large Cap', 'Mid Cap', 'Small Cap', 'Hybrid', 'ELSS']
fund_categories = {name: np.random.choice(categories) for name in fund_names}

nav_data = []
for name in fund_names:
    drift = np.random.uniform(0.08, 0.15) / TRADING_DAYS
    vol = np.random.uniform(0.12, 0.25) / np.sqrt(TRADING_DAYS)
    nav = 100
    for i, d in enumerate(all_dates):
        if i > 0:
            ret = drift + vol * np.random.normal(0, 1)
            nav = nav * (1 + ret)
        nav_data.append([name, d, nav, fund_categories[name]])

df_nav = pd.DataFrame(nav_data, columns=['scheme_name', 'date', 'nav', 'category'])
df_nav['date'] = pd.to_datetime(df_nav['date'])
print("NAV data generated.")

# Compute daily returns
df_nav = df_nav.sort_values(['scheme_name', 'date'])
df_nav['daily_return'] = df_nav.groupby('scheme_name')['nav'].pct_change().fillna(0)
print("Daily returns computed.")

# ============================================
# 2. CAGR (1yr, 3yr, 5yr)
# ============================================
def calc_cagr(group):
    group = group.sort_values('date')
    end_nav = group['nav'].iloc[-1]
    end_date = group['date'].iloc[-1]
    
    def get_nav_ago(days):
        target = end_date - timedelta(days=days)
        sub = group[group['date'] >= target]
        return sub['nav'].iloc[0] if len(sub) > 0 else np.nan
    
    nav_1y = get_nav_ago(365)
    nav_3y = get_nav_ago(3*365)
    nav_5y = get_nav_ago(5*365)
    
    cagr_1y = (end_nav / nav_1y) - 1 if not np.isnan(nav_1y) else np.nan
    cagr_3y = (end_nav / nav_3y)**(1/3) - 1 if not np.isnan(nav_3y) else np.nan
    cagr_5y = (end_nav / nav_5y)**(1/5) - 1 if not np.isnan(nav_5y) else np.nan
    return pd.Series({'cagr_1y': cagr_1y, 'cagr_3y': cagr_3y, 'cagr_5y': cagr_5y})

cagr_df = df_nav.groupby('scheme_name').apply(calc_cagr).reset_index()
cagr_df['category'] = cagr_df['scheme_name'].map(fund_categories)

# ============================================
# 3. Sharpe Ratio
# ============================================
def sharpe_ratio(returns_series):
    excess = returns_series - (RISK_FREE_RATE / TRADING_DAYS)
    if excess.std() == 0:
        return 0
    return (excess.mean() / excess.std()) * np.sqrt(TRADING_DAYS)

sharpe_series = df_nav.groupby('scheme_name')['daily_return'].apply(sharpe_ratio)
sharpe_df = sharpe_series.reset_index()
sharpe_df.columns = ['scheme_name', 'sharpe_ratio']
sharpe_df['category'] = sharpe_df['scheme_name'].map(fund_categories)

# ============================================
# 4. Sortino Ratio
# ============================================
def sortino_ratio(returns_series):
    excess = returns_series - (RISK_FREE_RATE / TRADING_DAYS)
    negative = excess[excess < 0]
    downside_std = negative.std() if len(negative) > 0 else 0.01
    return (excess.mean() / downside_std) * np.sqrt(TRADING_DAYS)

sortino_series = df_nav.groupby('scheme_name')['daily_return'].apply(sortino_ratio)
sortino_df = sortino_series.reset_index()
sortino_df.columns = ['scheme_name', 'sortino_ratio']
sortino_df['category'] = sortino_df['scheme_name'].map(fund_categories)

# ============================================
# 5. Alpha & Beta (vs simulated Nifty 100)
# ============================================
np.random.seed(42)
market_returns = np.random.normal(0.0004, 0.01, len(all_dates))
df_market = pd.DataFrame({'date': all_dates, 'market_return': market_returns})

alpha_beta_list = []
for name in df_nav['scheme_name'].unique():
    fund = df_nav[df_nav['scheme_name'] == name][['date', 'daily_return']].copy()
    merged = pd.merge(fund, df_market, on='date').dropna()
    if len(merged) < 10:
        continue
    slope, intercept, r_val, p_val, std_err = stats.linregress(merged['market_return'], merged['daily_return'])
    alpha_annual = intercept * TRADING_DAYS
    beta = slope
    alpha_beta_list.append({'scheme_name': name, 'alpha': alpha_annual, 'beta': beta, 'r_squared': r_val**2})

alpha_beta_df = pd.DataFrame(alpha_beta_list)

# ============================================
# 6. Maximum Drawdown
# ============================================
def max_drawdown(group):
    group = group.sort_values('date')
    nav = group['nav'].values
    running_max = np.maximum.accumulate(nav)
    dd = (nav - running_max) / running_max
    min_dd = dd.min()
    trough_idx = np.argmin(dd)
    peak_idx = np.argmax(nav[:trough_idx+1]) if trough_idx > 0 else 0
    return {
        'max_drawdown': min_dd,
        'peak_date': group['date'].iloc[peak_idx],
        'trough_date': group['date'].iloc[trough_idx]
    }

dd_data = []
for name in df_nav['scheme_name'].unique():
    fund = df_nav[df_nav['scheme_name'] == name]
    res = max_drawdown(fund)
    res['scheme_name'] = name
    res['category'] = fund_categories[name]
    dd_data.append(res)

dd_df = pd.DataFrame(dd_data)

# ============================================
# 7. Build Fund Scorecard
# ============================================
# Merge all metrics using the correct column name 'cagr_3y'
score = cagr_df[['scheme_name', 'cagr_3y']].copy()
score = score.merge(sharpe_df[['scheme_name', 'sharpe_ratio']], on='scheme_name', how='left')
score = score.merge(alpha_beta_df[['scheme_name', 'alpha']], on='scheme_name', how='left')
score = score.merge(sortino_df[['scheme_name', 'sortino_ratio']], on='scheme_name', how='left')
score = score.merge(dd_df[['scheme_name', 'max_drawdown']], on='scheme_name', how='left')

# Simulate expense ratio for each scheme
np.random.seed(123)
unique_schemes = score['scheme_name'].unique()
expense_map = {name: np.random.uniform(0.5, 2.5) for name in unique_schemes}
score['expense_ratio'] = score['scheme_name'].map(expense_map)

# Fill missing values with median (if any)
for col in ['cagr_3y', 'sharpe_ratio', 'alpha', 'max_drawdown']:
    score[col] = score[col].fillna(score[col].median())

# Ranks (lower rank = better)
score['cagr_rank'] = score['cagr_3y'].rank(ascending=False)
score['sharpe_rank'] = score['sharpe_ratio'].rank(ascending=False)
score['alpha_rank'] = score['alpha'].rank(ascending=False)
score['expense_rank'] = score['expense_ratio'].rank(ascending=True)   # lower expense better
score['dd_rank'] = score['max_drawdown'].rank(ascending=True)         # lower drawdown better

# Normalize to 0–100 (higher score = better)
max_rank = len(score)
for col in ['cagr_rank', 'sharpe_rank', 'alpha_rank', 'expense_rank', 'dd_rank']:
    if max_rank > 1:
        score[f'{col}_score'] = (1 - (score[col] - 1) / (max_rank - 1)) * 100
    else:
        score[f'{col}_score'] = 100.0

# Weighted total
score['total_score'] = (0.30 * score['cagr_rank_score'] +
                        0.25 * score['sharpe_rank_score'] +
                        0.20 * score['alpha_rank_score'] +
                        0.15 * score['expense_rank_score'] +
                        0.10 * score['dd_rank_score'])

score = score.sort_values('total_score', ascending=False)
score['overall_rank'] = range(1, len(score)+1)

print("\nTop 10 funds by overall score:")
print(score[['scheme_name', 'total_score', 'overall_rank', 'cagr_3y', 'sharpe_ratio', 'alpha', 'expense_ratio', 'max_drawdown']].head(10))

# ============================================
# 8. Save to CSV
# ============================================
os.makedirs('data/processed', exist_ok=True)
score.to_csv('data/processed/fund_scorecard.csv', index=False)
print("\nFund scorecard saved to data/processed/fund_scorecard.csv")