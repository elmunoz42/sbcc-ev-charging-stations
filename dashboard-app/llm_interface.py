import requests
import json
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

# Default values
DEFAULT_MODEL = 'claude-3-opus-20240229'
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

def describe_dataset_with_claude(df, api_key=None, model=DEFAULT_MODEL, 
                                version='2023-06-01', custom_prompt=CUSTOM_PROMPT, 
                                column_description=COLUMN_DESCRIPTION, column_info_file=None):
    """
    Function to analyze a dataset using pandas describe() and then interpret the results using Claude API.
    
    Parameters:
    df (pandas.DataFrame): The dataset to analyze
    api_key (str): Anthropic API key
    model (str, optional): Claude model to use (default: 'claude-3-opus-20240229')
    version (str, optional): Anthropic API version (default: '2023-06-01')
    custom_prompt (str, optional): Custom instructions for Claude
    column_description (str, optional): Description of columns to provide context to Claude
    column_info_file (str, optional): Path to a text file containing column descriptions
    
    Returns:
    str: Claude's interpretation of the dataset statistics
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
    
    # Prepare the prompt for Claude
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
    
    {column_info}
    
    Here is the statistical summary of the dataset:
    {json.dumps(dataset_info, default=json_serialize, indent=2)}
    """
    
    # API endpoint for Claude
    api_url = "https://api.anthropic.com/v1/messages"
    
    # Use provided API key or fall back to environment variable
    if api_key is None:
        api_key = CLAUDE_API_KEY
        if api_key is None:
            return "Error: No API key provided and CLAUDE_API_KEY environment variable not set"
            
    # Prepare the request
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": version
    }
    
    data = {
        "model": model,
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    # Make the API request
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        
        # Extract Claude's response
        claude_response = response.json()
        interpretation = claude_response['content'][0]['text']
        
        return interpretation
    
    except Exception as e:
        return f"Error calling Claude API: {str(e)}"