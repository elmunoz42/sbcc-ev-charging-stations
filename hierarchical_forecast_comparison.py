import warnings
warnings.filterwarnings("ignore")

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard-app'))

import numpy as np
import pandas as pd
from model import train_model, generate_forecast
from sklearn.metrics import mean_squared_error, mean_absolute_error

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

# This is the single source of truth used by BOTH approaches, so the
# comparison is apples-to-apples (not confounded by the days-report file
# possibly having different filtering than the sessions file)
total_series = daily_site.sum(axis=1)
total_series.name = 'Energy delivered (kWh)'

sites = daily_site.columns.tolist()
print(f"Series length: {len(total_series)} days, {len(sites)} sites")
print(f"Sites: {sites}")

def mape(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / np.where(y_true == 0, np.nan, y_true))) * 100

def to_model_df(series):
    return pd.DataFrame({'Energy delivered (kWh)': series})

def safe_forecast(series, horizon):
    """Wraps train_model/generate_forecast; returns a flat zero forecast for
    degenerate (all-zero or near-constant) site histories rather than letting
    ARIMA choke on them."""
    if series.std() < 1e-6:
        idx = pd.date_range(series.index[-1] + pd.Timedelta(days=1), periods=horizon, freq='D')
        return pd.Series(series.iloc[-1], index=idx)
    try:
        m = train_model(to_model_df(series))
        f = generate_forecast(m, to_model_df(series), months=int(horizon / 30))
        return f['forecast'].clip(lower=0)
    except Exception as e:
        print(f"    [site model failed: {e} -- falling back to flat last-value forecast]")
        idx = pd.date_range(series.index[-1] + pd.Timedelta(days=1), periods=horizon, freq='D')
        return pd.Series(max(series.iloc[-30:].mean(), 0), index=idx)

HORIZON = 90
origins = [700, 790, 880, 970]

results = {'Top-down (county total)': [], 'Bottom-up (sum of per-site forecasts)': []}

for fold_i, origin in enumerate(origins):
    train_total = total_series.iloc[:origin]
    test_total = total_series.iloc[origin:origin + HORIZON]
    print(f"\n--- Fold {fold_i+1}: train=[:{origin}], test={test_total.index.min().date()} to {test_total.index.max().date()} ---")

    # Top-down: forecast the aggregated total directly
    f_top = safe_forecast(train_total, HORIZON)
    rmse_top = np.sqrt(mean_squared_error(test_total.values, f_top.values))
    mape_top = mape(test_total.values, f_top.values)
    print(f"  Top-down      RMSE={rmse_top:7.2f}  MAPE={mape_top:5.2f}%")
    results['Top-down (county total)'].append((rmse_top, mape_top))

    # Bottom-up: forecast each site, then sum
    site_forecasts = []
    for site in sites:
        train_site = daily_site[site].iloc[:origin]
        f_site = safe_forecast(train_site, HORIZON)
        site_forecasts.append(f_site.values)
    bottom_up_total = np.sum(site_forecasts, axis=0)
    bottom_up_total = np.clip(bottom_up_total, 0, None)

    rmse_bu = np.sqrt(mean_squared_error(test_total.values, bottom_up_total))
    mape_bu = mape(test_total.values, bottom_up_total)
    print(f"  Bottom-up     RMSE={rmse_bu:7.2f}  MAPE={mape_bu:5.2f}%")
    results['Bottom-up (sum of per-site forecasts)'].append((rmse_bu, mape_bu))

print("\n" + "="*70)
print("SUMMARY (mean +/- std across folds)")
print("="*70)
for name, vals in results.items():
    rmses = [v[0] for v in vals]
    mapes = [v[1] for v in vals]
    print(f"{name:40s} RMSE mean={np.mean(rmses):7.2f} std={np.std(rmses):6.2f}   MAPE mean={np.mean(mapes):5.2f}% std={np.std(mapes):5.2f}%")
