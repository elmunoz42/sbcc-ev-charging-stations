# app.py (Main Streamlit Application)
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from model import process_data, train_model, generate_forecast
from visualization import plot_historical_data, plot_forecast

# Import Claude API function - handle if import fails
try:
    from llm_interface import describe_dataset_with_claude
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    st.error("Claude API integration is unavailable. Make sure to install the required packages.")

def main():
    st.title("EV Energy Delivery Forecast Tool")
    st.write("Upload your CSV data to forecast energy delivery for the next three months")
    
    # File input section with a description
    st.write("Choose your data source:")
    
    # Create columns for file upload and sample data download
    col1, col2 = st.columns([3, 1])
    
    # File upload in the first column
    with col1:
        uploaded_file = st.file_uploader("Upload CSB Daily PowerFlex-Axcess CSV File", type="csv")
    
    # Sample data download button in the second column
    with col2:
        st.write("Don't have data?")
        sample_file_path = "CSB-Daily-Data-2020-01-01_2024-12-31.csv"
        
        # Check if sample file exists
        if os.path.exists(sample_file_path):
            # Read file for download
            try:
                with open(sample_file_path, "r") as f:
                    sample_data = f.read()
                    
                # Filter out comment lines for the downloadable version
                lines = [line for line in sample_data.split('\n') if not line.strip().startswith('//')]
                filtered_sample = '\n'.join(lines)
                
                st.download_button(
                    label="⬇️ Download Sample CSV",
                    data=filtered_sample,
                    file_name="EV-Daily-Data-Sample.csv",
                    mime="text/csv",
                    key="download_sample_btn"
                )
            except Exception as e:
                st.error(f"Error reading sample file: {e}")
        else:
            st.error("Sample data file not found.")
    
    # Process data based on user choice
    df = None
    
    if uploaded_file is not None:
        # Process the uploaded file
        try:
            # Skip any lines that start with '//' instead of using the comment parameter
            # First read as text to filter out comment lines
            content = uploaded_file.getvalue().decode('utf-8')
            lines = [line for line in content.split('\n') if not line.strip().startswith('//')]
            filtered_content = '\n'.join(lines)
            
            # Now parse the filtered content
            import io
            df = pd.read_csv(io.StringIO(filtered_content))
            st.success("File uploaded successfully!")
            
        except Exception as e:
            st.error(f"Error processing file: {e}")
            st.write("Please ensure your CSV file has the correct format.")
    
    # If we have data (either from sample or upload), process it
    if df is not None:
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
        
        # Create two columns for buttons
        btn_col1, btn_col2 = st.columns(2)
        
        # AI Analysis Button in first column
        with btn_col1:
            if LLM_AVAILABLE:
                analysis_button = st.button("Generate AI Analysis", key="ai_analysis_btn")
                if analysis_button:
                    with st.spinner("Analyzing data with Claude AI..."):
                        try:
                            # Create a clean copy of the dataframe for analysis
                            analysis_df = df.copy()
                            
                            # Make sure columns are properly formatted for analysis
                            # Convert numeric columns that might be strings
                            for col in analysis_df.columns:
                                if col != 'Day':  # Skip the date column
                                    try:
                                        # Handle specific problematic columns
                                        if col in ['Max kW hour (kW)']:
                                            # Skip columns that have text mixed with numbers
                                            continue
                                        analysis_df[col] = pd.to_numeric(analysis_df[col], errors='coerce')
                                    except:
                                        pass  # If conversion fails, leave as is
                            
                            # Show a simpler dataset to Claude - just numeric columns with valid data
                            # Select only numeric columns
                            numeric_cols = analysis_df.select_dtypes(include=['number']).columns.tolist()
                            
                            # Create a simplified dataframe with just the numeric columns
                            simple_df = analysis_df[numeric_cols].copy()
                            
                            # Remove columns with all NaN values
                            simple_df = simple_df.dropna(axis=1, how='all')
                            
                            # Use a hard-coded example API response when API key isn't available
                            if os.getenv('CLAUDE_API_KEY') is None:
                                analysis = """
                                ## Data Analysis Results
                                
                                * **Dataset Size**: The dataset contains energy delivery data records
                                * **Energy Delivered**: This appears to be the main metric of interest
                                * **Missing Values**: Several columns contain missing values that should be addressed
                                * **Recommendation**: Consider collecting more complete data for better analysis
                                
                                *Note: This is a mock analysis since no Claude API key was detected.*
                                """
                                st.warning("Using mock analysis - Claude API key not found")
                            else:
                                analysis = describe_dataset_with_claude(simple_df)
                            
                            st.markdown("### AI Data Analysis")
                            st.markdown(analysis)
                        except Exception as e:
                            st.error(f"Error generating AI analysis: {str(e)}")
                            st.info("Note: Make sure your Claude API key is properly configured in the .env file")
                            
                            # Show a detailed traceback for debugging
                            import traceback
                            st.error(f"Detailed error: {traceback.format_exc()}")
        
        # Generate Forecast button in second column
        with btn_col2:
            forecast_button = st.button("Generate Forecast", key="forecast_btn")
        
        # Train model and generate forecast if button clicked
        if forecast_button:
            with st.spinner("Training model and generating forecast..."):
                try:
                    model = train_model(processed_data)
                    forecast_data = generate_forecast(model, processed_data, months=3)
                except Exception as e:
                    st.error(f"Error generating forecast: {str(e)}")
                    st.info("This may be due to data format issues or insufficient data points for time series forecasting.")
                    forecast_data = None  # Set to None to avoid trying to display the forecast
                
                # Only display forecast if we have data
                if forecast_data is not None:
                    # Display forecast
                    st.subheader("3-Month Energy Delivery Forecast")
                    fig_forecast = plot_forecast(processed_data, forecast_data)
                    st.pyplot(fig_forecast)
                    
                    # Display forecast metrics
                    st.subheader("Forecast Statistics")
                    st.write(f"Average Daily Energy Forecast: {forecast_data['forecast'].mean():.2f} kWh")
                    st.write(f"Peak Energy Day: {forecast_data['forecast'].max():.2f} kWh")
                    
                    # Show top 10 peak forecast days
                    st.subheader("Top 10 Peak Energy Days")
                    top_peaks = forecast_data.sort_values(by='forecast', ascending=False).head(10)
                    
                    # Create a dataframe with the date and forecast value for better display
                    peak_df = pd.DataFrame({
                        'Date': top_peaks.index.strftime('%Y-%m-%d'),
                        'Day of Week': top_peaks.index.strftime('%A'),
                        'Forecasted Energy (kWh)': top_peaks['forecast'].round(2)
                    })
                    
                    # Display the top peaks as a table
                    st.table(peak_df)
                    
                    # Download forecast as CSV
                    st.download_button(
                        label="Download Forecast Data",
                        data=forecast_data.to_csv(index=True),
                        file_name="energy_forecast.csv",
                        mime="text/csv"
                    )

if __name__ == "__main__":
    main()