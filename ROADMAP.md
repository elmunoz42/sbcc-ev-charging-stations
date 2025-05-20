# Roadmap for Continous Support of CSB Zero-Emission Vehicle Plan

## Current Infrastructure: Streamlit Dashboard Application

### Interactive Forecasting and Monitoring Tool

The Streamlit dashboard application currently serves as the central deployment platform for the County of Santa Barbara's EV charging infrastructure forecasting. This interactive tool enables transportation department staff to upload PowerFlex charging data exports and receive immediate forecasts and insights without requiring technical expertise. The dashboard provides a critical interface between the data science models and the decision-makers responsible for implementing the Zero Emission Vehicle Plan.

*Current Capabilities:*
1. **Data Ingestion and Validation:** Accepts CSV exports from the PowerFlex system and automatically validates and processes the data to ensure compatibility with the forecasting models.
2. **Historical Data Visualization:** Generates interactive visualizations of historical charging patterns, including energy delivery trends, usage statistics, and seasonal variations.
3. **Time-Series Forecasting:** Utilizes STL-ARIMA models to generate three-month forecasts of daily energy demand (kWh), with clear confidence intervals to indicate prediction uncertainty.
4. **Demand Spike Detection:** Identifies potential periods of unusually high demand in the forecast, flagging them for infrastructure planning consideration.
5. **Export Capabilities:** Allows users to download forecast data and visualizations for inclusion in reports and presentations to stakeholders.

*Value to CSB:*
- **Accessibility:** Democratizes access to complex forecasting models, allowing non-technical staff to generate insights independently.
- **Decision Support:** Provides data-driven guidance for infrastructure planning and resource allocation decisions.
- **Continuous Learning:** Each new data upload improves the underlying models, increasing forecast accuracy over time.
- **Operational Efficiency:** Reduces the time between data collection and actionable insights from weeks to minutes.

## Future Improvement: Advanced Predictive Modeling and Strategic Placement

### Neural Network for Usage Spike Prediction

To further enhance the accuracy of predicting EV charging demand, especially during peak usage periods, a neural network model will be developed. This model will be trained on historical usage data, incorporating temporal patterns (time of day, day of week, seasonality) and other relevant features to identify and forecast sudden spikes in demand. This will enable proactive resource allocation and grid management.

*Response Strategy:*
1.  **Data Augmentation:** Collect and integrate additional data sources that might influence charging patterns, such as local events, weather data, and holiday schedules.
2.  **Feature Engineering:** Create relevant features for the neural network, such as lagged usage values, time-based indicators (e.g., hour of day, day of week as cyclical features), and event flags.
3.  **Model Selection and Training:** Experiment with different neural network architectures (e.g., LSTMs, GRUs, or simpler feedforward networks if sufficient) suited for time series forecasting. Train the model on the historical session and daily aggregated data.
4.  **Validation and Refinement:** Validate the model's ability to predict spikes on a hold-out dataset. Refine the model architecture and hyperparameters based on performance.

### Future Improvement: Demographic and Urban Planning Integration for Optimal Station Placement

To strategically determine the optimal locations for new charging stations and the expansion of existing ones, the project will incorporate demographic data and city planning information. This approach aims to ensure equitable access to charging infrastructure and align with future urban development.

*Response Strategy:*
1.  **Data Acquisition:**
    *   **New Zero-Emission Vehicle Data:** Integrate new vehicle population data as it becomes available from California Energy department [website](https://www.energy.ca.gov/data-reports/energy-almanac/.
    *   **Demographic Data:** Obtain census data or other demographic datasets for Santa Barbara County, including population density, income levels, vehicle ownership rates, and housing types (e.g., multi-unit dwellings vs. single-family homes).
    *   **City Planning Data:** Gather information on current and future zoning regulations, planned residential and commercial developments, public transportation routes, and major points of interest from the County's planning department.
2.  **Geospatial Analysis:**
    *   Map existing charging station locations.
    *   Overlay demographic data to identify areas with high potential EV adoption but currently underserved by charging infrastructure (e.g., densely populated areas with limited off-street parking).
    *   Incorporate city planning data to pinpoint locations that align with future growth, such as new housing developments, commercial centers, or public transit hubs.
3.  **Needs Assessment Model:** Develop a scoring or weighting system that combines forecasted demand (from the neural network and SARIMAX models), demographic indicators, and urban planning priorities to rank potential locations for new charging stations.
4.  **Accessibility and Equity Considerations:** Ensure that the placement strategy considers accessibility for all residents, including those in lower-income neighborhoods or areas with a higher proportion of renters who may lack home charging options. This aligns with the equity goals outlined in the CSB's "Zero Emission Vehicle Plan".
5.  **Scenario Planning:** Model different scenarios for charging station rollout based on budget constraints and phased development plans, providing CSB with a flexible and data-driven expansion strategy.