import json
import pandas as pd
import numpy as np
import os
import streamlit as st
import requests
import urllib.parse

# Default values
FALLBACK_ENDPOINT = "https://llama2-query-responder.fountain-city.workers.dev/"
CUSTOM_PROMPT = """
        You are an expert data analyst providing Zero-Emission Vehicle specialist actionable insight from data collected about charging station utilization over time. Based on the dataset statistics provided, give me a concise, 
        human-readable interpretation of the key characteristics of this dataset. Focus on:
        
        - Describe ONLY the Started Sessions, AVG session duration (minutes) and Energy delivered (kWh) columns.
        - NO MORE THANT 160 WORDS FOR THE RESPONSE
        """



def describe_dataset_with_fallback(df, custom_prompt=CUSTOM_PROMPT):
    """
    Function to analyze a dataset using pandas describe() and then interpret the results using the fallback API.
    
    Parameters:
    df (pandas.DataFrame): The dataset to analyze
    custom_prompt (str, optional): Custom instructions for the LLM
    column_description (str, optional): Description of columns to provide context
    column_info_file (str, optional): Path to a text file containing column descriptions
    
    Returns:
    str: LLM's interpretation of the dataset statistics
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        return "Error: Input must be a pandas DataFrame"
    
    if df.empty:
        return "Error: DataFrame is empty"
        
    # Get basic statistics - limit to numeric columns only for reliability
    try:
        stats = df.describe()
    except Exception as e:
        return f"Error calculating statistics: {str(e)}"
    
    # Get column data types
    dtypes = pd.DataFrame(df.dtypes, columns=['Data Type'])
    
    # Calculate null values
    null_counts = pd.DataFrame(df.isnull().sum(), columns=['Null Count'])
    null_percentages = pd.DataFrame(df.isnull().mean() * 100, columns=['Null Percentage'])
    
    # Count unique values for each column
    unique_counts = pd.DataFrame(df.nunique(), columns=['Unique Values'])
    
    # Combine all information
    # Convert all DataFrames to dictionaries with string-based keys
    def convert_dict_keys_to_str(d):
        if isinstance(d, dict):
            return {str(k): convert_dict_keys_to_str(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [convert_dict_keys_to_str(i) for i in d]
        else:
            return d
            
    # Create dataset info with string keys
    dataset_info = {
        'statistics': convert_dict_keys_to_str(stats.to_dict()),
        'data_types': convert_dict_keys_to_str(dtypes.to_dict()),
        'null_info': {
            'counts': convert_dict_keys_to_str(null_counts.to_dict()),
            'percentages': convert_dict_keys_to_str(null_percentages.to_dict())
        },
        'unique_values': convert_dict_keys_to_str(unique_counts.to_dict()),
        'sample_data': convert_dict_keys_to_str(df.head(5).to_dict())
    }

    
    # Prepare the prompt
    # Use a custom JSON serialization function that handles all types
    def json_serialize(obj):
        if hasattr(obj, 'isoformat'):  # Handle datetime objects
            return obj.isoformat()
        elif pd.isna(obj):  # Handle NaN, NaT, etc.
            return None
        else:
            return str(obj)
    
    prompt = f"""
    {custom_prompt}
    
    Here is the statistical summary of the dataset:
    {json.dumps(dataset_info, default=json_serialize, indent=2)}

    IMPORTANT: NO MORE THANT 160 WORDS FOR THE RESPONSE
    """
    
    # Use the fallback API
    try:
        # URL encode the prompt for GET request
        encoded_prompt = urllib.parse.quote(prompt)
        # Make the GET request to the fallback endpoint
        response = requests.get(f"{FALLBACK_ENDPOINT}?query={encoded_prompt}")
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()
            
            # Extract the interpretation from the response structure
            # This structure is based on the example you provided
            if isinstance(result, list) and len(result) > 0:
                if 'response' in result[0] and 'response' in result[0]['response']:
                    interpretation = result[0]['response']['response']
                    return interpretation + f"\n\n\n\n\n\n\n\n\n\nLlama 2 Fallback API Response"
            
            # If we couldn't find the expected structure, return the raw response
            return f"Received response but couldn't parse expected structure. Raw response: {result}"
        else:
            return f"Error: Fallback API request failed with status code {response.status_code}"
    
    except Exception as e:
        return f"Error calling fallback API: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Load a sample dataset if called directly
    try:
        # If this is run in Streamlit, provide a file uploader
        if 'st' in globals():
            st.title("Zero Emission Vehicle Data Analyzer")
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)
                
                if st.button("Analyze Dataset"):
                    with st.spinner("Analyzing dataset..."):
                        interpretation = describe_dataset_with_fallback(df)
                        st.markdown(interpretation)
        else:
            # If run directly as script, try to load a sample file
            sample_file = "sample_data.csv"
            if os.path.exists(sample_file):
                df = pd.read_csv(sample_file)
                interpretation = describe_dataset_with_fallback(df)
                print(interpretation)
            else:
                print(f"Sample file {sample_file} not found. Please provide a CSV file path.")
    except Exception as e:
        print(f"Error in main execution: {str(e)}")