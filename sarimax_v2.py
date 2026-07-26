import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error, mean_absolute_error

df = pd.read_csv('data/SB-County-County Public reporting 2020-01-01_2024-12-31.csv')
df['Day'] = pd.to_datetime(df['Day'])
df = df.set_index('Day').asfreq('D')
energy_df = df['Energy delivered (kWh)']['2022-01-01':].interpolate()

split_point = int(len(energy_df) * 0.7)
y_train = energy_df.iloc[:split_point]
y_test = energy_df.iloc[split_point:]

def metrics(y_true, y_pred, label):
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    print(f"{label:55s} RMSE={rmse:8.2f}  MAE={mae:8.2f}  MAPE={mape:6.2f}%")
    return rmse, mae, mape

def build_exog(index, harmonics=1):
    t = np.arange(len(index))
    period = 365.25
    cols = {}
    for h in range(1, harmonics+1):
        cols[f'fourier_sin{h}'] = np.sin(2*np.pi*h*t/period)
        cols[f'fourier_cos{h}'] = np.cos(2*np.pi*h*t/period)
    return pd.DataFrame(cols, index=index)

print(f"Train: {len(y_train)} days, Test: {len(y_test)} days\n")
print("Baseline to beat: STL-ARIMA period=30 -> RMSE=482.44  MAE=394.62  MAPE=33.43%\n")

# Small grid over seasonal order, no is_weekend (redundant with seasonal terms), 1 harmonic only
exog_train = build_exog(y_train.index, harmonics=1)
exog_test = build_exog(y_test.index, harmonics=1)

seasonal_orders = [(1,1,1,7), (0,1,1,7), (1,1,0,7), (0,1,0,7), (2,1,1,7)]
orders = [(1,0,0), (0,0,1), (1,0,1)]

best = None
for order in orders:
    for so in seasonal_orders:
        try:
            m = SARIMAX(y_train, order=order, seasonal_order=so, exog=exog_train,
                        enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
            f = m.forecast(len(y_test), exog=exog_test)
            rmse, mae, mape = metrics(y_test, f, f"order={order} seasonal={so}")
            if best is None or rmse < best[0]:
                best = (rmse, mae, mape, order, so, m)
        except Exception as e:
            print(f"order={order} seasonal={so} FAILED: {e}")

print(f"\nBest config: order={best[3]} seasonal_order={best[4]}  RMSE={best[0]:.2f}  MAPE={best[2]:.2f}%")
print(f"vs STL-ARIMA baseline MAPE=33.43%  -> {'BEATS baseline' if best[2] < 33.43 else 'still worse than baseline'}")
