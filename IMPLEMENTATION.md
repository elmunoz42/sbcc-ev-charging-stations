# Implementation Guide: Supporting the County of Santa Barbara Zero Emission Vehicle Plan

## Using the Dashboard Application

The Streamlit dashboard application serves as the primary tool for transportation department staff to interact with the EV charging data and forecasting models. This interactive tool provides valuable insights to support the County of Santa Barbara's Zero Emission Vehicle Plan implementation.

### Accessing the Deployed Dashboard

The dashboard application has been deployed and is accessible online at:

**[https://zero-emission-vehicle-data-analyzer-csb.streamlit.app/](https://zero-emission-vehicle-data-analyzer-csb.streamlit.app/)**

This deployment allows County of Santa Barbara staff to use the forecasting tools without needing to set up a local development environment. Simply visit the URL in your web browser to access the full functionality of the dashboard.

For testing purposes there is a sample CSV file that can be downloaded and uploaded to the app to see the app working.

### Preparing PowerFlex Data for Analysis

To get the most accurate forecasts and insights from the dashboard, follow these steps to export your PowerFlex charging station data:

1. **Accessing PowerFlex Reporting System**:
   * Log in to the County's PowerFlex management portal
   * Navigate to the "Reports" section
   * Select "Daily Reporting" view

2. **Exporting Daily Utilization Data**:
   * Set the date range to cover at least the last 12 months of data (longer periods will improve forecast accuracy)
   * Select the CSV export option
   * Ensure all relevant charging stations are included in the export
   * Save the exported CSV file to your local computer

3. **Data Format Requirements**:
   * The dashboard expects the standard PowerFlex daily reporting format
   * Key fields should include date, energy delivered (kWh), session counts, and duration metrics
   * If you've customized your PowerFlex reports, ensure they include at minimum the date and energy delivery data

4. **Uploading to the Dashboard**:
   * Once you have your CSV export, navigate to the dashboard application
   * Use the file upload feature on the main page
   * The system will automatically validate and process your data

### Using the Dashboard for Decision Support

1. **Data Upload and Analysis**:
   * Upload the latest PowerFlex CSV export of daily reporting for EV charging data utilization
   * Click the upload button and select your CSV file exported from the PowerFlex system
   * Use the sample data provided if you need to familiarize yourself with the dashboard first
   * Review the historical data visualizations to identify usage patterns and trends

2. **Generating Forecasts**:
   * Click the "Generate Forecast" button to create a three-month forecast of energy demand
   * Review the forecast charts and tables to identify future demand patterns
   * Pay attention to confidence intervals to understand the forecast uncertainty

3. **AI-Powered Analysis**:
   * Use the "Generate AI Analysis" feature to get natural language insights about the data
   * This feature automatically highlights significant trends and anomalies

4. **Decision Support for ZEV Plan Goals**:
   * Use forecast data to project charging infrastructure needs as EV adoption increases
   * Identify potential capacity constraints before they impact service levels
   * Support the planning process for the 375 new publicly available charging stations goal

## Making Data-Driven Decisions

The dashboard application is designed to support several key decision-making processes within the Zero Emission Vehicle Plan implementation:

### 1. Capacity Planning

Use the forecast data to answer critical questions such as:
- How many additional charging stations are needed to meet projected demand in 6-12 months?
- Which existing stations are approaching capacity constraints?
- What will be the peak energy demand for new installations?

### 2. Policy Optimization

The dashboard provides insights to inform policy decisions:
- Identify optimal time limits for charging sessions based on actual usage patterns
- Determine pricing structures that maximize throughput while maintaining accessibility
- Evaluate the impact of existing policies on charging station utilization

### 3. Progress Reporting

Generate data-backed reports for stakeholders:
- Track progress toward the Climate Action Plan's EV adoption goals
- Demonstrate the impact of infrastructure investments on EV usage
- Show trends in charging station utilization over time

### 4. Budget Justification

Support budget requests with concrete data:
- Quantify the need for additional infrastructure based on growth trends
- Identify locations where upgrades will provide the greatest return on investment
- Project future energy costs and revenue based on usage forecasts

## Collaboration and Sharing

The dashboard supports collaborative decision-making through:

1. **Exportable Reports**: All visualizations and forecasts can be downloaded for inclusion in presentations and reports
2. **Shareable Insights**: Generate summaries that can be shared with stakeholders and policymakers
3. **Consistent Metrics**: Establish a standard set of key performance indicators for measuring progress

## Leveraging the Time Series Models

The project includes a trained STL-ARIMA model that can be used independently from the dashboard for more advanced analyses.

### Loading the Pre-trained Model

```python
import pickle

# Load the saved model
with open('stlf_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

# Use the loaded model to make forecasts
forecast30 = loaded_model.forecast(30)  # Generate a 30-day forecast
```

### Advanced Model Applications

1. **Scenario Testing**:
   * Test different EV adoption growth scenarios by adjusting the forecast parameters
   * Model the impact of seasonal events or policy changes on charging demand

2. **Infrastructure Planning**:
   * Calculate required capacity for new charging stations based on growth projections
   * Identify optimal placement of new stations by analyzing demand patterns by location

3. **Policy Development**:
   * Use idle time analysis from the decision tree model to develop evidence-based policies
   * Determine optimal time limits and fee structures to maximize charging station utilization

4. **Progress Tracking**:
   * Monitor actual energy delivery against forecasted values
   * Track progress toward the CAP goal of increasing passenger EV ownership to 25% by 2030

## Integration with Zero Emission Vehicle Plan

The forecasting models and dashboard directly support several key components of the Zero Emission Vehicle Plan:

1. **Charging Infrastructure Expansion**:
   * Provides data-driven justification for the placement and capacity of new charging stations
   * Helps prioritize infrastructure investments to meet the 375 public chargers goal
   * Generates projections that can be included in funding proposals and grant applications

2. **EV Adoption Tracking**:
   * Correlates charging station usage with EV adoption rates
   * Provides early indicators of progress toward the 25% passenger EV ownership goal

3. **Resource Optimization**:
   * Identifies opportunities to increase capacity through policy changes (e.g., reducing idle time)
   * Maximizes the impact of limited infrastructure funding

## Future Improvements

As outlined in the ROADMAP.md file, several enhancements are planned:

1. **Neural Network for Usage Spike Prediction**:
   * More accurate prediction of demand spikes
   * Better handling of anomalous events and seasonal variations

2. **Demographic and Urban Planning Integration**:
   * Data-driven station placement recommendations
   * Equity-focused infrastructure planning

3. **Interactive Scenario Planning**:
   * Allow users to model different EV adoption scenarios
   * Visualize impacts of policy changes on infrastructure requirements