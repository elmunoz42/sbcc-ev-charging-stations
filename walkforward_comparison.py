import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.forecasting.stl import STLForecast
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.seasonal import MSTL
from sklearn.metrics import mean_squared_error, mean_absolute_error

df = pd.read_csv('data/SB-County-County Public reporting 2020-01-01_2024-12-31.csv')
df['Day'] = pd.to_datetime(df['Day'])
df = df.set_index('Day').asfreq('D')
energy_df = df['Energy delivered (kWh)']['2022-01-01':].interpolate()
print(f"Total series length: {len(energy_df)} days ({energy_df.index.min().date()} to {energy_df.index.max().date()})")

HORIZON = 90
origins = [700, 790, 880, 970]  # expanding-window walk-forward origins
print(f"Walk-forward folds (expanding window, {HORIZON}-day test each): origins={origins}\n")

def mape(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def build_fourier(index, harmonics=1, period=365.25, t0=0):
    t = np.arange(len(index)) + t0
    cols = {}
    for h in range(1, harmonics+1):
        cols[f'fs{h}'] = np.sin(2*np.pi*h*t/period)
        cols[f'fc{h}'] = np.cos(2*np.pi*h*t/period)
    return pd.DataFrame(cols, index=index)

results = {'STL-ARIMA': [], 'SARIMAX': [], 'MSTL-ARIMA': []}

for fold_i, origin in enumerate(origins):
    y_train = energy_df.iloc[:origin]
    y_test = energy_df.iloc[origin:origin+HORIZON]
    print(f"--- Fold {fold_i+1}: train=[:{origin}] ({len(y_train)} days), test=[{origin}:{origin+HORIZON}] ({y_test.index.min().date()} to {y_test.index.max().date()}) ---")

    # 1. STL-ARIMA period=30 (author's baseline)
    stlf = STLForecast(y_train, ARIMA, model_kwargs={'order': (1,1,0), 'trend': 't'}, period=30).fit()
    f_stl = stlf.forecast(HORIZON)
    rmse = np.sqrt(mean_squared_error(y_test, f_stl)); m = mape(y_test, f_stl)
    print(f"  STL-ARIMA     RMSE={rmse:7.2f}  MAPE={m:5.2f}%")
    results['STL-ARIMA'].append((rmse, m))

    # 2. SARIMAX(0,0,1)x(1,1,0,7) + 1-harmonic annual Fourier (best config from grid search)
    exog_train = build_fourier(y_train.index, harmonics=1)
    exog_test = build_fourier(y_test.index, harmonics=1, t0=len(y_train))
    try:
        m_sx = SARIMAX(y_train, order=(0,0,1), seasonal_order=(1,1,0,7), exog=exog_train,
                        enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
        f_sx = m_sx.forecast(HORIZON, exog=exog_test)
        rmse = np.sqrt(mean_squared_error(y_test, f_sx)); m = mape(y_test, f_sx)
        print(f"  SARIMAX       RMSE={rmse:7.2f}  MAPE={m:5.2f}%")
        results['SARIMAX'].append((rmse, m))
    except Exception as e:
        print(f"  SARIMAX FAILED: {e}")

    # 3. MSTL-ARIMA: decompose with periods=[7,365], ARIMA on trend+resid, naive-repeat both seasonal components
    try:
        mstl = MSTL(y_train, periods=[7, 365]).fit()
        trend = mstl.trend
        seasonal = mstl.seasonal  # DataFrame with columns seasonal_7, seasonal_365
        resid = mstl.resid
        deseasonalized = trend + resid
        arima_fit = ARIMA(deseasonalized, order=(1,1,0), trend='t').fit()
        f_deseason = arima_fit.forecast(HORIZON)

        # repeat last observed full cycle forward for each seasonal component
        def repeat_seasonal(seasonal_col, period, horizon):
            last_cycle = seasonal_col.iloc[-period:].values
            reps = int(np.ceil(horizon / period))
            tiled = np.tile(last_cycle, reps)[:horizon]
            return tiled

        s7 = repeat_seasonal(seasonal['seasonal_7'], 7, HORIZON)
        s365 = repeat_seasonal(seasonal['seasonal_365'], 365, HORIZON)
        f_mstl = f_deseason.values + s7 + s365
        rmse = np.sqrt(mean_squared_error(y_test, f_mstl)); m = mape(y_test, f_mstl)
        print(f"  MSTL-ARIMA    RMSE={rmse:7.2f}  MAPE={m:5.2f}%")
        results['MSTL-ARIMA'].append((rmse, m))
    except Exception as e:
        print(f"  MSTL-ARIMA FAILED: {e}")
    print()

print("="*70)
print("SUMMARY (mean +/- std across folds)")
print("="*70)
for name, vals in results.items():
    if not vals:
        print(f"{name:15s} no successful folds")
        continue
    rmses = [v[0] for v in vals]
    mapes = [v[1] for v in vals]
    print(f"{name:15s} RMSE mean={np.mean(rmses):7.2f} std={np.std(rmses):6.2f}   MAPE mean={np.mean(mapes):5.2f}% std={np.std(mapes):5.2f}%")
