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
    try:
        # First try the new implementation
        from llm_interface_new import describe_dataset_with_claude
        LLM_AVAILABLE = True
    except ImportError:
        # Fall back to original implementation if new one is not available
        from llm_interface import describe_dataset_with_claude
        LLM_AVAILABLE = True
    
    # Also import fallback module for direct access if needed
    try:
        from llm_fallback import describe_dataset_with_fallback
        FALLBACK_AVAILABLE = True
    except ImportError:
        FALLBACK_AVAILABLE = False
except ImportError:
    LLM_AVAILABLE = False
    FALLBACK_AVAILABLE = False
    st.error("Claude API integration is unavailable. Make sure to install the required packages.")

def main():
    st.title("EV Energy Delivery Forecast Tool (Beta)")
    st.header("Upload your CSV data to forecast energy delivery for the next three months")
    
    # Show app version info with fallback support
    st.sidebar.info("Version 0.1.0 - Added LLM Fallback Support when Claude API is unavailable")
    
    # Display available LLM systems in sidebar
    st.sidebar.subheader("LLM System Status")
    if LLM_AVAILABLE:
        st.sidebar.success("✅ Claude API available")
    else:
        st.sidebar.error("❌ Claude API unavailable")
    
    if FALLBACK_AVAILABLE:
        st.sidebar.success("✅ Fallback LLM available")
    else:
        st.sidebar.error("❌ Fallback LLM unavailable")
    
    # Debug: Check if secrets are loaded
    if st.sidebar.checkbox("Debug Secrets", False):
        try:
            st.sidebar.write("Secrets Configuration:")
            if "CLAUDE_API_KEY" in st.secrets:
                st.sidebar.success("✅ Claude API Key found")
                # Show first/last few chars of the key for verification without exposing it
                api_key = st.secrets["CLAUDE_API_KEY"]
                masked_key = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 10 else "***masked***"
                st.sidebar.text(f"API Key: {masked_key}")
                
                # Provide info about API key format
                st.sidebar.info("API Key Format: Claude API keys typically start with 'sk-ant-' and should not have quotes in the secrets.toml file.")
                
                # Test API connection
                if st.sidebar.button("Test API Connection"):
                    with st.sidebar:
                        with st.spinner("Testing connection to Claude API..."):
                            try:
                                import anthropic
                                # Initialize the Anthropic client
                                client = anthropic.Anthropic(api_key=api_key)
                                
                                # List available models to test connection
                                models = client.models.list()
                                
                                st.success("✅ API connection successful!")
                                st.write("Available models:")
                                
                                # Display available models in a more readable format
                                model_data = []
                                for model in models.data:
                                    model_data.append({
                                        "name": model.name,
                                        "description": getattr(model, "description", "No description available")
                                    })
                                
                                st.table(model_data)
                            except Exception as e:
                                st.error(f"❌ Error testing API: {str(e)}")
            else:
                st.sidebar.error("❌ Claude API Key not found")
                st.sidebar.text("Check your .streamlit/secrets.toml file")
        except Exception as e:
            st.sidebar.error(f"Error checking secrets: {str(e)}")
    
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
                                if col == 'Day':  
                                    # Ensure date column is properly formatted
                                    try:
                                        analysis_df[col] = pd.to_datetime(analysis_df[col], errors='coerce')
                                    except:
                                        pass
                                else:
                                    try:
                                        # Handle specific problematic columns
                                        if col in ['Max kW hour (kW)', 'Max Utilization (%)', 'Faulted Stations', 'Uptime (%)']:
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
                            
                            # Handle the API analysis
                            try:
                                # Call Claude API for analysis
                                analysis = describe_dataset_with_claude(simple_df)
                                
                                # Check for different types of errors that would trigger fallback
                                if analysis and any(err in analysis for err in ["Error: No API key provided", "Error calling Claude API: 401", "Error calling Claude API", "authentication", "unauthorized"]):
                                    st.warning("Claude API issue detected. Trying fallback LLM...")
                                    
                                    # Only try fallback if it's available
                                    if FALLBACK_AVAILABLE:
                                        try:
                                            # Call the fallback LLM
                                            with st.spinner("Using fallback LLM service..."):
                                                analysis = describe_dataset_with_fallback(simple_df)
                                                st.success("✅ Analysis generated using fallback LLM")
                                        except Exception as fallback_error:
                                            st.error(f"Fallback LLM also failed: {str(fallback_error)}")
                                            # Provide a mock analysis as last resort
                                            analysis = """
                                            ## Data Analysis Results
                                            
                                            * **Dataset Size**: The dataset contains energy delivery data records
                                            * **Energy Delivered**: This appears to be the main metric of interest
                                            * **Missing Values**: Several columns contain missing values that should be addressed
                                            * **Recommendation**: Consider collecting more complete data for better analysis
                                            
                                            *Note: This is a mock analysis since both Claude API and fallback service failed.*
                                            """
                                    else:
                                        st.error("Fallback LLM not available")
                                        # Provide a mock analysis as fallback
                                        analysis = """
                                        ## Data Analysis Results
                                        
                                        * **Dataset Size**: The dataset contains energy delivery data records
                                        * **Energy Delivered**: This appears to be the main metric of interest
                                        * **Missing Values**: Several columns contain missing values that should be addressed
                                        * **Recommendation**: Consider collecting more complete data for better analysis
                                        
                                        *Note: This is a mock analysis since the Claude API key was not correctly configured.*
                                        """
                            except Exception as e:
                                st.error(f"Error during analysis: {str(e)}")
                                
                                # Try fallback if main analysis fails
                                if FALLBACK_AVAILABLE:
                                    try:
                                        st.warning("Main analysis failed. Trying fallback LLM...")
                                        with st.spinner("Using fallback LLM service..."):
                                            analysis = describe_dataset_with_fallback(simple_df)
                                            st.success("✅ Analysis generated using fallback LLM")
                                    except Exception as fallback_error:
                                        st.error(f"Fallback LLM also failed: {str(fallback_error)}")
                                        analysis = "Error during analysis. All LLM services failed. Please check the application logs for more details."
                                else:
                                    analysis = "Error during analysis. Please check the application logs for more details."
                            
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