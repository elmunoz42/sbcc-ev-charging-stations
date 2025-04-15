import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def inspect_dataframe_column(dataframe, column):
    dataframe[column].value_counts()
    print(dataframe[column].value_counts())
    percentage_of_missing = dataframe[column].isnull().mean() * 100
    print(f"Percentage missing: {percentage_of_missing}")



def plot_dataframe_missing_values(dataframe, filepath):
    # Gets the mean of missing values in each column. Since True = 1 and False = 0 the mean tells us how much of the data is missing.
    missing_values = dataframe.isnull().mean().sort_values(ascending=False)
    
    # Create the bar plot
    plt.figure(figsize=(12, 6))
    missing_plot = missing_values.plot(kind='bar')
    
    # Customize the plot
    plt.xlabel('Columns')
    plt.ylabel('Number of Missing Values')
    plt.title('Missing Value Ratio per Column (Sorted)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Show the plot
    plt.show()
    plt.savefig(filepath)

def calculate_percentage_difference(value1, value2):
    """
    Calculate the percentage difference between two values using NumPy.
    
    Args:
    value1 (float): First value
    value2 (float): Second value
    
    Returns:
    float: Percentage difference between the two values
    """
    return np.abs(value1 - value2) / np.mean([value1, value2]) * 100

def calculate_percentage_change(original_value, new_value):
    """
    Calculate the percentage change between two values using NumPy.
    
    Args:
    original_value (float): The original value
    new_value (float): The new value
    
    Returns:
    float: Percentage change from the original value to the new value
    """
    return (new_value - original_value) / original_value * 100

def describe_dataset_with_claude(df, api_key, model='claude-3-opus-20240229', 
                                version='2023-06-01', custom_prompt=None, 
                                column_description=None, column_info_file=None):
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
    # Get basic statistics
    stats = df.describe(include='all')
    
    # Get column data types
    dtypes = pd.DataFrame(df.dtypes, columns=['Data Type'])
    
    # Calculate null values
    null_counts = pd.DataFrame(df.isnull().sum(), columns=['Null Count'])
    null_percentages = pd.DataFrame(df.isnull().mean() * 100, columns=['Null Percentage'])
    
    # Count unique values for each column
    unique_counts = pd.DataFrame(df.nunique(), columns=['Unique Values'])
    
    # Combine all information
    dataset_info = {
        'statistics': stats.to_dict(),
        'data_types': dtypes.to_dict(),
        'null_info': {
            'counts': null_counts.to_dict(),
            'percentages': null_percentages.to_dict()
        },
        'unique_values': unique_counts.to_dict(),
        'sample_data': df.head(5).to_dict()
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
    prompt = f"""
    {custom_prompt}
    
    {column_info}
    
    Here is the statistical summary of the dataset:
    {json.dumps(dataset_info, default=str, indent=2)}
    """
    
    # API endpoint for Claude
    api_url = "https://api.anthropic.com/v1/messages"
    
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