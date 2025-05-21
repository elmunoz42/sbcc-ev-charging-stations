import requests
import json
import pandas as pd
import numpy as np
import os
import streamlit as st
from openai import OpenAI

# Default values
DEFAULT_MODEL = 'gpt-4o'
CUSTOM_PROMPT = """
        You are an expert data analyst providing Zero-Emission Vehicle specialist actionable insight from data collected about charging station utilization over time. Based on the dataset statistics provided, give me a concise, 
        human-readable interpretation of the key characteristics of this dataset. Focus on:
        
        1. The typical values and ranges for numerical columns
        2. Ignore the categorical features since you don't have data for these. DONT DESCRIBE FEATURES FOR WHICH YOU DON'T HAVE NUMBERS.
        4. Any interesting patterns or insights
        
        Format your response as bullet points that are easy to read and understand.
        Make your insights actionable for further data analysis and classification model development.
        """

COLUMN_DESCRIPTION = """
        Day: Date of recorded charging station activity
        Started Sessions: Number of charging sessions initiated during the day
        Completed Sessions: Number of charging sessions successfully completed during the day
        Microsessions: Number of very short charging sessions (likely less than a few minutes)
        AVG session duration (minutes): Average total time vehicles were connected to chargers
        AVG charging duration (minutes): Average time vehicles were actively drawing power
        AVG session idle (minutes): Average time vehicles remained connected after charging completed
        Energy delivered (kWh): Total electrical energy provided to vehicles
        AVG kWh delivered per session (kWh): Average amount of energy delivered per charging session
        Max kWh delivered per session (kWh): Maximum amount of energy delivered in a single charging session
        Max kW hour (kW): Hour of the day with peak power demand
        GHGs avoided (lbs): Estimated greenhouse gas emissions avoided by using electric vs. gasoline vehicles
        Gasoline avoided (Gal): Estimated gallons of gasoline not consumed due to EV usage
        Electric miles provided (mi): Estimated electric vehicle miles enabled by the energy delivered
        Potential revenue ($): Maximum possible revenue based on pricing policies
        Collected revenue ($): Actual revenue collected from charging sessions
        Discounts granted ($): Value of discounts or promotions applied to charging sessions
        Utilization (%): Percentage of time charging stations were in use
        Max Utilization (%): Time period with highest utilization percentage
        Faulted Stations: Stations experiencing technical issues or malfunctions
        Time in Faulted State (hours): Duration stations were non-operational due to faults
        Uptime (%): Percentage of time stations were operational and available for use
        """

def describe_dataset_with_openai(df, api_key=None, model=DEFAULT_MODEL, 
                               custom_prompt=CUSTOM_PROMPT, 
                               column_description=COLUMN_DESCRIPTION, column_info_file=None):
    """
    Function to analyze a dataset using pandas describe() and then interpret the results using OpenAI API.
    
    Parameters:
    df (pandas.DataFrame): The dataset to analyze
    api_key (str): OpenAI API key
    model (str, optional): OpenAI model to use (default: 'gpt-4o')
    custom_prompt (str, optional): Custom instructions for OpenAI
    column_description (str, optional): Description of columns to provide context to OpenAI
    column_info_file (str, optional): Path to a text file containing column descriptions
    
    Returns:
    str: OpenAI's interpretation of the dataset statistics
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
    
    # Default prompt if none is provided
    if custom_prompt is None:
        custom_prompt = """
        You are an expert data analyst. Based on the dataset statistics provided, give me a concise, 
        human-readable interpretation of the key characteristics of this dataset. Focus on:
        
        1. The typical values and ranges for numerical columns
        2. The distribution of categorical columns
        3. Any potential issues with the data (e.g., missing values, outliers)
        4. Any interesting patterns or insights
        
        Format your response as bullet points that are easy to read and understand.
        Make your insights actionable for a business context.
        """
    
    # Get column description from file if specified
    if column_info_file and os.path.exists(column_info_file):
        with open(column_info_file, 'r') as f:
            column_description = f.read()
    
    # Add column description to the prompt if provided
    column_info = ""
    if column_description:
        column_info = f"""
        Here is additional information about the columns in this dataset:
        {column_description}
        
        Please use this information to better understand the context and meaning of each column.
        """
    
    # Prepare the prompt
    # Use a custom JSON serialization function that handles all types
    def json_serialize(obj):
        if hasattr(obj, 'isoformat'):  # Handle datetime objects
            return obj.isoformat()
        elif pd.isna(obj):  # Handle NaN, NaT, etc.
            return None
        else:
            return str(obj)
    
    prompt_content = f"""
    {custom_prompt}
    
    {column_info}
    
    Here is the statistical summary of the dataset:
    {json.dumps(dataset_info, default=json_serialize, indent=2)}
    """
    
    # Get API key from Streamlit secrets
    if api_key is None:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except Exception as e:
            return f"Error: Unable to access API key from secrets: {str(e)}"
            
    # Make the API request using the official OpenAI client
    try:
        # Initialize the OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create the chat completion request
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert data analyst providing insightful analysis."},
                {"role": "user", "content": prompt_content}
            ],
            max_tokens=2048,
            temperature=0.7
        )
        
        # Extract OpenAI's response
        interpretation = response.choices[0].message.content
        
        return interpretation
    
    except Exception as e:
        error_msg = str(e)
        # Check if the error is an authentication error
        if "401" in error_msg or "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower() or "invalid api key" in error_msg.lower():
            # Log the error before trying fallback
            fallback_msg = "OpenAI API returned authentication error. Using fallback LLM..."
            print(fallback_msg)
            
            try:
                # Import the fallback module here to avoid circular imports
                from llm_fallback import describe_dataset_with_fallback
                
                # Call the fallback with the same DataFrame
                return describe_dataset_with_fallback(df, custom_prompt=custom_prompt)
            except Exception as fallback_error:
                return f"Error calling OpenAI API: {error_msg}. Fallback also failed: {str(fallback_error)}"
        
        return f"Error calling OpenAI API: {error_msg}"
