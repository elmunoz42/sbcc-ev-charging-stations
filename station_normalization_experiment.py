import warnings
warnings.filterwarnings("ignore")

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard-app'))

import numpy as np
import pandas as pd
from model import train_model, generate_forecast
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.stattools import adfuller

# ---- Build total daily kWh series (same source as the hierarchical experiments,
# so all three station-splitting/normalization experiments share one ground truth) ----
df = pd.read_csv('data/SB-County-County-Public-Portfolio-stations-report-01_01_20-12_31_24.csv',
                  usecols=['Session start', 'kWh delivered', 'EVSEID (PFID)'])
df['Session start'] = pd.to_datetime(df['Session start'], format='%m-%d-%Y %H:%M:%S', errors='coerce')
df = df.dropna(subset=['Session start'])
df = df[df['Session start'] >= '2022-01-01']
df['date'] = df['Session start'].dt.normalize()

daily_total = df.groupby('date')['kWh delivered'].sum()
full_index = pd.date_range(daily_total.index.min(), daily_total.index.max(), freq='D')
daily_total = daily_total.reindex(full_index, fill_value=0.0)
daily_total.name = 'Energy delivered (kWh)'

# ---- Build cumulative "stations live as of date" series ----
first_seen = df.groupby('EVSEID (PFID)')['Session start'].min().dt.normalize()
first_seen_counts = first_seen.value_counts().sort_index()
station_count = first_seen_counts.reindex(full_index, fill_value=0).cumsum()
station_count = station_count.replace(0, np.nan).ffill().fillna(method='bfill')  # in case day 0 has 0

print(f"Series length: {len(daily_total)} days")
print(f"Station count: {station_count.iloc[0]:.0f} at start -> {station_count.iloc[-1]:.0f} at end")

# ---- Stationarity check: is the per-station rate less trending than the raw total? ----
per_station = daily_total / station_count
print(f"\nADF test (lower/more negative = more stationary, less trending):")
adf_raw = adfuller(daily_total)
adf_norm = adfuller(per_station)
print(f"  Raw total kWh:     ADF stat={adf_raw[0]:7.3f}  p-value={adf_raw[1]:.4f}")
print(f"  kWh per station:   ADF stat={adf_norm[0]:7.3f}  p-value={adf_norm[1]:.4f}")

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

results = {'Raw total (current approach)': [], 'Normalized (per-station rate x held-constant station count)': []}

for fold_i, origin in enumerate(origins):
    train_raw = daily_total.iloc[:origin]
    test_raw = daily_total.iloc[origin:origin + HORIZON]
    print(f"\n--- Fold {fold_i+1}: train=[:{origin}], test={test_raw.index.min().date()} to {test_raw.index.max().date()} ---")

    # Approach A: forecast raw total directly
    f_raw = safe_forecast(train_raw, HORIZON)
    rmse_raw = np.sqrt(mean_squared_error(test_raw.values, f_raw.values))
    mape_raw = mape(test_raw.values, f_raw.values)
    print(f"  Raw total                RMSE={rmse_raw:7.2f}  MAPE={mape_raw:5.2f}%")
    results['Raw total (current approach)'].append((rmse_raw, mape_raw))

    # Approach B: forecast per-station rate, multiply back by station count
    # held constant at the last known value (reasonable for a 90-day horizon)
    train_norm = (daily_total / station_count).iloc[:origin]
    f_norm_rate = safe_forecast(train_norm, HORIZON)
    last_station_count = station_count.iloc[origin - 1]
    f_norm_total = f_norm_rate.values * last_station_count

    rmse_norm = np.sqrt(mean_squared_error(test_raw.values, f_norm_total))
    mape_norm = mape(test_raw.values, f_norm_total)
    print(f"  Normalized (x{last_station_count:.0f} stations)   RMSE={rmse_norm:7.2f}  MAPE={mape_norm:5.2f}%")
    results['Normalized (per-station rate x held-constant station count)'].append((rmse_norm, mape_norm))

print("\n" + "="*70)
print("SUMMARY (mean +/- std across folds)")
print("="*70)
for name, vals in results.items():
    rmses = [v[0] for v in vals]
    mapes = [v[1] for v in vals]
    print(f"{name:60s} RMSE mean={np.mean(rmses):7.2f} std={np.std(rmses):6.2f}   MAPE mean={np.mean(mapes):5.2f}% std={np.std(mapes):5.2f}%")
