import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.forecasting.stl import STLForecast
from sklearn.metrics import mean_squared_error, mean_absolute_error

# ---- Replicate the notebook's exact preprocessing pipeline ----
df = pd.read_csv('data/SB-County-County Public reporting 2020-01-01_2024-12-31.csv')
df['Day'] = pd.to_datetime(df['Day'])
df = df.set_index('Day').asfreq('D')

energy_df = df['Energy delivered (kWh)']['2022-01-01':]
energy_df = energy_df.interpolate()  # fill any gaps from asfreq, same spirit as model.py

split_point = int(len(energy_df) * 0.7)
y_train = energy_df.iloc[:split_point]
y_test = energy_df.iloc[split_point:]

print(f"Train range: {y_train.index.min().date()} to {y_train.index.max().date()} ({len(y_train)} days)")
print(f"Test range:  {y_test.index.min().date()} to {y_test.index.max().date()} ({len(y_test)} days)")

def metrics(y_true, y_pred, label):
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    print(f"\n{label}")
    print(f"  RMSE: {rmse:.2f}")
    print(f"  MAE:  {mae:.2f}")
    print(f"  MAPE: {mape:.2f}%")
    return rmse, mae, mape

# ---- Baseline 1: plain ARIMA(1,1,0) ----
m1 = ARIMA(y_train, order=(1,1,0)).fit()
f1 = m1.forecast(len(y_test))
metrics(y_test, f1, "ARIMA(1,1,0) [baseline]")

# ---- Baseline 2: STL-ARIMA period=30 (author's chosen config) ----
stlf = STLForecast(y_train, ARIMA, model_kwargs={'order': (1,1,0), 'trend': 't'}, period=30)
stlf_res = stlf.fit()
f2 = stlf_res.forecast(len(y_test))
metrics(y_test, f2, "STL-ARIMA period=30 [author's baseline]")

# ---- New model: SARIMAX(1,1,0)x(1,1,1,7) + weekend flag + annual Fourier terms ----
def build_exog(index):
    t = np.arange(len(index))
    is_weekend = (index.dayofweek >= 5).astype(float)
    period = 365.25
    exog = pd.DataFrame({
        'is_weekend': is_weekend,
        'fourier_sin1': np.sin(2*np.pi*1*t/period),
        'fourier_cos1': np.cos(2*np.pi*1*t/period),
        'fourier_sin2': np.sin(2*np.pi*2*t/period),
        'fourier_cos2': np.cos(2*np.pi*2*t/period),
    }, index=index)
    return exog

exog_train = build_exog(y_train.index)
exog_test = build_exog(y_test.index)

m3 = SARIMAX(y_train, order=(1,1,0), seasonal_order=(1,1,1,7),
             exog=exog_train, enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
f3 = m3.forecast(len(y_test), exog=exog_test)
metrics(y_test, f3, "SARIMAX(1,1,0)x(1,1,1,7) + weekend + annual Fourier [new]")

print("\n" + m3.summary().tables[1].as_text())

print("\n--- Diagnosing forecast trajectory (does it diverge?) ---")
for i in [0, 10, 30, 60, 120, 200, 328]:
    print(f"  step {i:>3} | actual={y_test.iloc[i]:>10.1f} | pred={f3.iloc[i]:>12.1f}")

print("\n--- Trying a corrected config: d=0, seasonal D=1 only, trend handled by seasonal diff ---")
m4 = SARIMAX(y_train, order=(1,0,0), seasonal_order=(1,1,1,7),
             exog=exog_train, enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
f4 = m4.forecast(len(y_test), exog=exog_test)
metrics(y_test, f4, "SARIMAX(1,0,0)x(1,1,1,7) + weekend + Fourier [d=0 fix attempt]")
for i in [0, 10, 30, 60, 120, 200, 328]:
    print(f"  step {i:>3} | actual={y_test.iloc[i]:>10.1f} | pred={f4.iloc[i]:>12.1f}")
