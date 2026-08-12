import warnings
warnings.filterwarnings("ignore")

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard-app'))

import numpy as np
import pandas as pd
from model import train_model, generate_forecast
from sklearn.metrics import mean_squared_error, mean_absolute_error

TOP_K = 4  # number of biggest sites to model individually; rest bucket into "Other"

# ---- Build a site x date daily kWh matrix from the sessions-level data ----
df = pd.read_csv('data/SB-County-County-Public-Portfolio-stations-report-01_01_20-12_31_24.csv',
                  usecols=['Session start', 'kWh delivered', 'Site'])
df['Session start'] = pd.to_datetime(df['Session start'], format='%m-%d-%Y %H:%M:%S', errors='coerce')
df = df.dropna(subset=['Session start'])
df = df[df['Session start'] >= '2022-01-01']
df['date'] = df['Session start'].dt.normalize()

daily_site = df.groupby(['Site', 'date'])['kWh delivered'].sum().unstack('Site').fillna(0.0)
full_index = pd.date_range(daily_site.index.min(), daily_site.index.max(), freq='D')
daily_site = daily_site.reindex(full_index, fill_value=0.0)

total_series = daily_site.sum(axis=1)
total_series.name = 'Energy delivered (kWh)'
sites = daily_site.columns.tolist()
print(f"Series length: {len(total_series)} days, {len(sites)} sites, TOP_K={TOP_K}")

def mape(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / np.where(y_true == 0, np.nan, y_true))) * 100

def to_model_df(series):
    return pd.DataFrame({'Energy delivered (kWh)': series})

def safe_forecast(series, horizon):
    if series.std() < 1e-6:
        idx = pd.date_range(series.index[-1] + pd.Timedelta(days=1), periods=horizon, freq='D')
        return pd.Series(series.iloc[-1], index=idx)
    try:
        m = train_model(to_model_df(series))
        f = generate_forecast(m, to_model_df(series), months=int(horizon / 30))
        return f['forecast'].clip(lower=0)
    except Exception as e:
        print(f"    [model failed: {e} -- flat fallback]")
        idx = pd.date_range(series.index[-1] + pd.Timedelta(days=1), periods=horizon, freq='D')
        return pd.Series(max(series.iloc[-30:].mean(), 0), index=idx)

HORIZON = 90
origins = [700, 790, 880, 970]

results = {
    'Top-down (county total)': [],
    'Bottom-up (16 sites)': [],
    f'Hybrid (top-{TOP_K} sites + Other bucket)': [],
}

for fold_i, origin in enumerate(origins):
    train_total = total_series.iloc[:origin]
    test_total = total_series.iloc[origin:origin + HORIZON]
    print(f"\n--- Fold {fold_i+1}: train=[:{origin}], test={test_total.index.min().date()} to {test_total.index.max().date()} ---")

    # Top-down
    f_top = safe_forecast(train_total, HORIZON)
    rmse_top = np.sqrt(mean_squared_error(test_total.values, f_top.values))
    mape_top = mape(test_total.values, f_top.values)
    print(f"  Top-down                RMSE={rmse_top:7.2f}  MAPE={mape_top:5.2f}%")
    results['Top-down (county total)'].append((rmse_top, mape_top))

    # Rank sites by volume using ONLY the training window (no lookahead)
    train_matrix = daily_site.iloc[:origin]
    ranked_sites = train_matrix.sum(axis=0).sort_values(ascending=False).index.tolist()
    top_sites = ranked_sites[:TOP_K]
    other_sites = ranked_sites[TOP_K:]
    print(f"  Top-{TOP_K} sites this fold: {top_sites}")

    # Bottom-up (all 16 sites individually)
    site_forecasts_all = []
    for site in sites:
        f_site = safe_forecast(daily_site[site].iloc[:origin], HORIZON)
        site_forecasts_all.append(f_site.values)
    bottom_up_total = np.clip(np.sum(site_forecasts_all, axis=0), 0, None)
    rmse_bu = np.sqrt(mean_squared_error(test_total.values, bottom_up_total))
    mape_bu = mape(test_total.values, bottom_up_total)
    print(f"  Bottom-up (16 sites)     RMSE={rmse_bu:7.2f}  MAPE={mape_bu:5.2f}%")
    results['Bottom-up (16 sites)'].append((rmse_bu, mape_bu))

    # Hybrid: top-K sites individually + "Other" bucket (sum of remaining sites) as one series
    hybrid_forecasts = []
    for site in top_sites:
        f_site = safe_forecast(daily_site[site].iloc[:origin], HORIZON)
        hybrid_forecasts.append(f_site.values)
    other_series = daily_site[other_sites].iloc[:origin].sum(axis=1)
    other_series.name = 'Energy delivered (kWh)'
    f_other = safe_forecast(other_series, HORIZON)
    hybrid_forecasts.append(f_other.values)
    hybrid_total = np.clip(np.sum(hybrid_forecasts, axis=0), 0, None)
    rmse_hy = np.sqrt(mean_squared_error(test_total.values, hybrid_total))
    mape_hy = mape(test_total.values, hybrid_total)
    print(f"  Hybrid (top-{TOP_K}+Other)      RMSE={rmse_hy:7.2f}  MAPE={mape_hy:5.2f}%")
    results[f'Hybrid (top-{TOP_K} sites + Other bucket)'].append((rmse_hy, mape_hy))

print("\n" + "="*70)
print("SUMMARY (mean +/- std across folds)")
print("="*70)
for name, vals in results.items():
    rmses = [v[0] for v in vals]
    mapes = [v[1] for v in vals]
    print(f"{name:40s} RMSE mean={np.mean(rmses):7.2f} std={np.std(rmses):6.2f}   MAPE mean={np.mean(mapes):5.2f}% std={np.std(mapes):5.2f}%")
