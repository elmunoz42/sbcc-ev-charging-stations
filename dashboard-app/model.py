# model.py
import pandas as pd
import numpy as np

def process_data(df):
    """
    Preprocess the uploaded CSV data to prepare it for modeling.
    This function handles date conversion, missing values, and prepares
    the data in the format needed for the STL-ARIMA model.
    """
    # Check if the expected columns exist (similar to the ones in original dataset)
    expected_cols = ['Energy delivered (kWh)', 'Day']
    
    # If 'Day' column doesn't exist but the first column looks like a date
    if 'Day' not in df.columns:
        if 'Date' in df.columns:
            df.rename(columns={'Date': 'Day'}, inplace=True)
        else:
            # Try to check if first column might be a date
            try:
                pd.to_datetime(df.iloc[:, 0])
                df.rename(columns={df.columns[0]: 'Day'}, inplace=True)
            except:
                pass
    
    # Look for energy column with flexible naming
    energy_col = None
    for col in df.columns:
        if 'energy' in col.lower() or 'kwh' in col.lower() or 'delivered' in col.lower():
            energy_col = col
            break
    
    if energy_col and energy_col != 'Energy delivered (kWh)':
        df.rename(columns={energy_col: 'Energy delivered (kWh)'}, inplace=True)
    
    # Check if we have the required columns after renaming attempts
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}. Please check your CSV format.")
    
    # Convert date column to datetime
    df['Day'] = pd.to_datetime(df['Day'])
    
    # Set the Day column as the index
    df.set_index('Day', inplace=True)
    
    # Handle missing values in Energy delivered column
    if df['Energy delivered (kWh)'].isna().any():
        # Fill missing values with interpolation
        df['Energy delivered (kWh)'] = df['Energy delivered (kWh)'].interpolate()
    
    # Sort by date index
    df = df.sort_index()
    
    return df

def train_model(data):
    """
    Train an STL-ARIMA model on the processed data
    Parameters:
    - data: DataFrame with 'Energy delivered (kWh)' column and datetime index
    
    Returns:
    - Fitted STL-ARIMA model
    """
    try:
        from statsmodels.tsa.forecasting.stl import STLForecast
        from statsmodels.tsa.arima.model import ARIMA
        
        # Extract energy data
        energy_df = data['Energy delivered (kWh)']
        
        # Train STL model
        stlf = STLForecast(energy_df, ARIMA, 
                          model_kwargs={'order': (1, 1, 0), 'trend': "t"}, 
                          period=30)
        stlf_results = stlf.fit()
        
        return stlf_results
    except Exception as e:
        raise Exception(f"Error training model: {str(e)}. Please check if your data has the right format.")

def generate_forecast(model, data, months=3):
    """
    Generate forecasts for the specified number of months
    
    Parameters:
    - model: Fitted STL-ARIMA model
    - data: DataFrame with datetime index
    - months: Number of months to forecast
    
    Returns:
    - DataFrame with forecast values and datetime index
    """
    try:
        # Generate forecast for specified number of months
        forecast_horizon = 30 * months  # Approx. days in months
        forecast = model.forecast(forecast_horizon)
        
        # Create future date index
        last_date = data.index[-1]
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), 
                                    periods=forecast_horizon, freq='D')
        
        # Create forecast dataframe
        forecast_df = pd.DataFrame({
            'forecast': forecast
        }, index=future_dates)
        
        return forecast_df
    except Exception as e:
        raise Exception(f"Error generating forecast: {str(e)}.")