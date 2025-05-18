# visualization.py
import matplotlib.pyplot as plt
import seaborn as sns

def plot_historical_data(data):
    # Create plot of historical energy data
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data.index, data['Energy delivered (kWh)'], '--o')
    ax.set_title('Historical Energy Delivered (kWh)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Energy (kWh)')
    ax.grid(True)
    fig.tight_layout()
    
    return fig

def plot_forecast(historical_data, forecast_data):
    # Create plot combining historical data and forecast
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot historical data
    ax.plot(historical_data.index, historical_data['Energy delivered (kWh)'], 
            label='Historical Data', color='blue')
    
    # Plot forecast
    ax.plot(forecast_data.index, forecast_data['forecast'], 
            label='Forecast', color='red')
    
    # Add vertical line at forecast start
    ax.axvline(x=historical_data.index[-1], color='black', 
               linestyle='--', label='Forecast Start')
    
    ax.set_title('Energy Delivered (kWh) - 3 Month Forecast')
    ax.set_xlabel('Date')
    ax.set_ylabel('Energy (kWh)')
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    
    return fig