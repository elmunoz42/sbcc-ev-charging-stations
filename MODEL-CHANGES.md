# Model change: STL-ARIMA → MSTL-ARIMA

**Date:** 2026-07-20
**Files changed:** `dashboard-app/model.py`
**Status:** Implemented and smoke-tested against the full 2022-2024 dataset; not yet re-deployed to the live Streamlit app.

## Summary

The dashboard's forecasting model (`train_model()` / `generate_forecast()` in `dashboard-app/model.py`) was switched from **STL-ARIMA with a single 30-day seasonal period** to **MSTL-ARIMA with two seasonal periods (7-day and 365-day)**. Under a realistic evaluation (90-day forecast horizon, walk-forward cross-validation — matching how the "Generate Forecast" button is actually used), the new model cuts average forecast error roughly in half and is far more consistent run to run.

| Model | Mean MAPE (90-day horizon, 4-fold walk-forward CV) | Std dev across folds |
|---|---|---|
| STL-ARIMA, period=30 (previous) | 44.0% | ±26.4 |
| SARIMAX(0,0,1)×(1,1,0,7) + annual Fourier terms | 32.8% | ±19.9 |
| **MSTL-ARIMA, periods=[7, 365] (new)** | **22.3%** | **±2.7** |

## Why this changed

The original model selection (STL-ARIMA, period=30, chosen in `data-analysis-days.ipynb`) was validated with a **single fixed 70/30 train/test split**, evaluated on an ~11-month test window. That evaluation was misleading in two ways:

1. **The test horizon (329 days) didn't match real usage.** The dashboard's "Generate Forecast" button always requests a 3-month (~90-day) forecast (`IMPLEMENTATION.md`, `app.py:347`). A model can look best at an 11-month horizon and worst at a 3-month horizon, because the components that matter shift — over a horizon that long, a flexible trend extraction matters more than short-term/weekly dynamics.
2. **A single train/test split is a high-variance estimate.** Re-running the comparison as 4-fold walk-forward CV (expanding training window, fixed 90-day test window per fold) showed STL-ARIMA's MAPE swinging from 25.8% to 89.4% depending on which 90-day window it was asked to predict (std dev ±26.4). The original "STL-ARIMA wins" conclusion was an artifact of one favorable test window, not a stable result.

A site-level breakdown of the Sessions dataset also confirmed a real, strong weekly pattern exists in the aggregate data (county-wide weekday charging is ~59 percentage points busier than weekend charging — driven mostly by large government office sites like SB Admin and SB Health Services). STL-ARIMA's single period=30 setting never captured this weekly signal at all; MSTL captures both the weekly and annual cycles simultaneously.

### What was tried and rejected along the way

- **SARIMAX(1,1,0)×(1,1,1,7)** with `is_weekend` + annual Fourier-term exogenous regressors: forecast **diverged to negative energy values** over the 329-day test horizon due to double differencing (non-seasonal `d=1` stacked with seasonal `D=1`). Root-caused and fixed by dropping `d` to 0.
- **SARIMAX(0,0,1)×(1,1,0,7)** (fixed, best of a 15-config grid search) on the original 329-day single-split evaluation: stable, but still worse than STL-ARIMA (38.4% vs 33.4% MAPE) under that (misleading) evaluation.
- Under the corrected 90-day walk-forward evaluation, this same SARIMAX config actually beats STL-ARIMA (32.8% vs 44.0%) — but MSTL-ARIMA beats both.

Reproduction scripts for all of the above live in the repo root: `sarimax_experiment.py`, `sarimax_v2.py`, `site_weekday_analysis.py`, `walkforward_comparison.py`.

## What changed in the code

`dashboard-app/model.py`:

- `train_model(data)` now:
  1. Decomposes the series with `statsmodels.tsa.seasonal.MSTL(energy_df, periods=[7, 365])` (weekly + annual).
  2. Fits `ARIMA(order=(1,1,0), trend='t')` on the deseasonalized series (`trend + resid`).
  3. Stores the **last observed cycle** of each seasonal component (7 values for weekly, 365 for annual).
  4. Returns a `dict` — `{'type': 'mstl', 'arima_fit': ..., 'seasonal_cycles': {...}}` — instead of a single fitted object, since there's no built-in `MSTLForecast` class in statsmodels (unlike `STLForecast`, which existed for the single-period case).

- `generate_forecast(model, data, months=3)` now branches on `model['type']`:
  - `'mstl'`: forecasts the deseasonalized series with ARIMA, then adds back each seasonal component by tiling its last observed cycle forward (the same naive-seasonal-repeat approach `STLForecast` used internally, just applied to two periods instead of one).
  - `'stl'`: unchanged behavior, used only as a fallback (see below).

- **Fallback logic for short uploads.** MSTL's annual component needs roughly 2 full years of data to estimate reliably — with less than that, the seasonal decomposition becomes unstable (see Known limitations). `train_model()` now checks the length of the uploaded series and adapts:
  - `< 60 days`: falls back to the original single-period STL-ARIMA (period scaled down to fit the data).
  - `60 days – 2 years`: uses MSTL with **weekly seasonality only** (`periods=[7]`), skipping the unreliable annual component.
  - `≥ 2 years`: full MSTL with both weekly and annual seasonality (`periods=[7, 365]`).

  This means county staff uploading a fresh, short PowerFlex export (the app's own docs suggest 12+ months as a minimum) still get a reasonable forecast instead of an error or a garbage annual estimate.

## Known limitations / things to watch

1. **MSTL's `.seasonal` output shape depends on how many periods you pass in.** With 2+ periods it's a DataFrame with one column per period (`seasonal_7`, `seasonal_365`); with exactly 1 period it silently becomes a plain `Series` instead. The initial implementation didn't account for this and raised `KeyError: 'seasonal_7'` on the weekly-only fallback path — found via the walk-forward CV script (one fold failed with the same error) and again while smoke-testing this change on a ~400-day slice. Fixed by branching on `len(periods)`.
2. **`stlf_model.pkl` at the repo root is now stale.** It was pickled from the old `STLForecast` object (see `IMPLEMENTATION.md`'s "Loading the Pre-trained Model" section) and is unrelated to the live dashboard, which always retrains from the uploaded CSV. Anyone relying on loading that pickle directly for standalone analysis should regenerate it from the new MSTL-ARIMA pipeline, or that section of `IMPLEMENTATION.md` should be updated/removed.
3. **The 2-year annual-seasonality threshold is a judgment call**, not a statistically derived cutoff — it was chosen because it's the smallest window where MSTL didn't visibly misbehave in testing. Worth revisiting once a few more years of PowerFlex data accumulate.
4. This change has **not been tested through the live Streamlit UI** — validation so far is calling `process_data` → `train_model` → `generate_forecast` directly with the same arguments `app.py` uses, confirming correct output shape, no NaNs, and sane forecast dates. Running it once through the actual deployed app before the next release is still worth doing.

## Suggested next steps

- Re-point `IMPLEMENTATION.md`'s pretrained-model section at a freshly pickled MSTL-ARIMA model, or remove it if that workflow isn't used.
- Consider normalizing energy delivered by active station count before modeling (station rollout over 2022-2024 is a trend confound this change doesn't address — see the earlier discussion thread for detail).
- Extend the site-level weekday finding into an explicit fleet-vs-public-usage flag, since the biggest-volume sites (SB Admin, SB Health Services, SB Jail) look like government commuter charging rather than public/tourist usage.
