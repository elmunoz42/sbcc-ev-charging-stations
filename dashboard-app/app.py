# app.py (Main Streamlit Application)
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from model import process_data, train_model, generate_forecast
from visualization import plot_historical_data, plot_forecast

def main():
    st.title("EV Energy Delivery Forecast Tool")
    st.write("Upload your CSV data to forecast energy delivery for the next three months")
    
    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        # Process the data
        try:
            df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
            
            # Display data summary
            st.subheader("Data Summary")
            st.write(df.head())
            st.write(f"Total records: {len(df)}")
            
            # Process data and check if it's valid
            processed_data = process_data(df)
            
            # Display historical data
            st.subheader("Historical Data")
            fig_historical = plot_historical_data(processed_data)
            st.pyplot(fig_historical)
            
            # Train model and generate forecast
            if st.button("Generate Forecast"):
                with st.spinner("Training model and generating forecast..."):
                    model = train_model(processed_data)
                    forecast_data = generate_forecast(model, processed_data, months=3)
                    
                    # Display forecast
                    st.subheader("3-Month Energy Delivery Forecast")
                    fig_forecast = plot_forecast(processed_data, forecast_data)
                    st.pyplot(fig_forecast)
                    
                    # Display forecast metrics
                    st.subheader("Forecast Statistics")
                    st.write(f"Average Daily Energy Forecast: {forecast_data['forecast'].mean():.2f} kWh")
                    st.write(f"Peak Energy Day: {forecast_data['forecast'].max():.2f} kWh")
                    
                    # Download forecast as CSV
                    st.download_button(
                        label="Download Forecast Data",
                        data=forecast_data.to_csv(index=True),
                        file_name="energy_forecast.csv",
                        mime="text/csv"
                    )
        
        except Exception as e:
            st.error(f"Error processing file: {e}")
            st.write("Please ensure your CSV file has the correct format.")

if __name__ == "__main__":
    main()