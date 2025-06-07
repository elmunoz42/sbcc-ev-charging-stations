# How Can the County of Santa Barbara's Electric Vehicle Charging Infrastructure Data Advance the Implementation of the Zero Emission Vehicle Plan? 

## Executive Summary

This ongoing research project analyzes historical electric vehicle (EV) charging data to support the County of Santa Barbara's Zero Emission Vehicle Plan. With transportation accounting for 48% of the County's greenhouse gas emissions and an ambitious goal to reduce community-wide emissions by 50% by 2030, optimizing EV charging infrastructure is critical to achieving climate targets.

The study examines four years (2020-2024) of charging station utilization data collected from the County's [PowerFlex](https://infohub.delltechnologies.com/en-us/t/powerflex-14/) reporting system. Two primary datasets were analyzed: a session-level dataset containing 88,919 individual charging events and a day-level dataset with 1,827 days of aggregated metrics.

### Key findings include:

- **Growth in Energy Demand**: PowerFlex time series data reveals a consistent upward trend in kilowatt-hours of energy delivered through charging stations, with identifiable seasonality patterns that have been captured in our forecasting models.
  
- **Accelerating EV Adoption**: California Energy Commission data demonstrates an exponential increase in battery electric vehicles, confirming the need for Santa Barbara County's ambitious infrastructure expansion plans.
  
- **Optimization Opportunities**: Decision tree analysis identified efficiency improvements that could complement new station construction—specifically, targeting the 6% of charging sessions with excessive idle times through policy adjustments could significantly increase existing infrastructure capacity.

### Deployed Streamlit Application With Forecasting and Custom LLM-Powered Statistical Analysis

[dashboard-app](https://zero-emission-vehicle-data-analyzer-csb.streamlit.app/)

The application allows specialists to get up-to-date forecasts and AI-generated statistical analysis. For more details, please review the IMPLEMENTATION.md file in this repository.

## Research Question

How can historical electric vehicle (EV) charging station utilization data be used to forecast future charging capacity needs and optimize charging station placement in the County of Santa Barbara to help meet the "Zero Emission Vehicle Plan" goals?

## Rationale

The County of Santa Barbara (CSB) has ambitious greenhouse gas emission goals. The following excerpt is from a document my CSB liaison Jerel Francisco is working on. The document is already in a public draft format and available on the [CSB's transportation commision website](https://www.countyofsb.org/3218/Transportation).

### County of Santa Barbara Zero Emission Vehicle Plan (Public Draft) - May 2025

#### URL: https://cosantabarbara.app.box.com/s/uyds828nxptcrtsjbqssyiu4rpps5odr
#### Excerpt:

"The County has been a leader in climate action, taking steps to reduce greenhouse gas (GHG) emissions and prepare for climate impacts. The 2030 Climate Action Plan (CAP) has a target to reduce community-wide emissions 50% by 2030 (below 2018 levels). On-road vehicle transportation accounts for 48% of the County's GHG emissions¹. As of 2022, zero emission vehicles (ZEV) make up less than 2% of all vehicles on the road in Santa Barbara County.

To meet State and local emission reduction targets, the CAP includes the following goals to reduce transportation-related emissions:

#### Table 1. 2030 Climate Action Plan Zero Emission Mobility Goals

| CAP Goal | 2030 Goal | 2045 Goal |
|----------|-----------|-----------|
| Increase passenger electric vehicle ownership | 25% | 90% |
| Increase commercial electric vehicle use | 15% | 75% |
| Install at least 375 publicly available electric vehicle chargers | 375 | NA |
| Decarbonize off-road equipment | 21% | 38% |
| Increase bike-mode share | 1% | 5% |

ZEV planning and implementation transects nearly all County operations and community functions, from fleet vehicles, building regulations, infrastructure, parking and energy management. It will require action from both internal County Departments and local community and municipal partners to help implement the Actions (page 31) identified in this plan."

### Hypothesis of How Data Analysis and Machine Learning Algorithms Can Help CSB's Goals

Given CSB's stated goals, a number of specific questions arise:

1) If CSB is to increase the passenger electric vehicle (EV) ownership to 25%, what impact does that have on energy utilization? Especially, what kinds of spikes should we expect?

*Response strategy:* By training a forecasting model, we will be able to get a sense of the rapid oscillations and seasonal peaks and troughs we expect to see, e.g., during tourist seasons, work commute rush, etc. One important consideration is that we will need to forecast the total number of passenger cars CSB will have by then compared to today to accurately predict the pertinent metrics for the 25% we are hoping will be EVs. In other words: If the current number of EVs requires a charging grid with a certain capacity, how much capacity will the future number of EVs require?

2) Are there ways to optimize the grid to meet more energy output demand by modifying public utilization policies?

*Response strategy:* We will review the sessions data with visualizations, coefficient matrices, and decision tree modeling and inference. This will enable a much deeper understanding of the factors that are at play and allow for effective policy recommendations. E.g., reducing the idling time allowance during peak hours from 4 to 2 hours before a penalty charge. Please note that any such policy change will need to thoroughly consider not just logistic impacts but also accessibility impact on the CSB's citizens, especially marginalized groups, as this is an imperative clearly stated in the "Zero Emission Vehicle Plan".

*Summary:* This capstone research paper will work to address these 2 items in turn. Additionally, we have already been providing CSB value in performing statistical analysis and visualizations for data that had never before been thoroughly explored. Our hope is that the timing coincides and findings from this report can actually inform CSB's "Zero Emission Vehicle Plan" official report that is being actively worked on by Jerel Francisco and his colleagues. Furthermore, there is a ROADMAP document with future improvements we plan to deploy in the next few months.
   
## Data Sources

CSB's charging stations are integrated with a PowerFlex reporting system with up-to-date utilization metrics. The historical charging station utilization data includes session times, idle times, and energy consumption. Jerel Francisco exported the data from January 1st 2020 to December 31st 2024 for two types of data exports:
- [Sessions](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data/SB-County-County-Public-Portfolio-stations-report-01_01_20-12_31_24.csv):
      - This data has 88,919 rows and 30 columns. Each row represents a unique charging session, with information about the charging site, session duration, energy usage, etc.
      - The samples include public and CSB fleet vehicle utilization. Since Jerel Francisco had particular interest in the public utilization of the resources, we filtered out for public usage only early in our analysis of this dataset.
- [Days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data/SB-County-County%20Public%20reporting%202020-01-01_2024-12-31.csv):
      - This data has 1,827 rows and 22 columns. Each row represents a day in the 4-year period with data aggregated from all charging sites with information about metric averages.
- [Cars](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-vehicle-population.ipynb):
      - This is data from the California Energy Commission [website](https://www.energy.ca.gov/data-reports/energy-almanac/zero-emission-vehicle-and-infrastructure-statistics-collection/light). It tracks the light-duty vehicle population in California. 

For a breakdown of all the features please review the respective feature catalogues:
- [Sessions](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/sessions-feature-catalogue.md)
- [Days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/days-feature-catalogue.md)
- [Cars](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/cars-feature-catalogue.md)

## Jupyter Notebooks

- PRIMARY NOTEBOOK FOR MODEL DEVELOPMENT: [data-analysis-days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-days.ipynb)
- EXPLORATORY NOTEBOOK: [data-analysis-sessions](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-sessions.ipynb)
- EXPLORATORY NOTEBOOK: [data-analysis-vehicle-population](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-vehicle-population.ipynb)
  
## Methodology

### CRISP-DM Framework

The project follows the Cross-Industry Standard Process for Data Mining (CRISP-DM) framework to ensure a structured and comprehensive approach:

- **Business Understanding**: Through extensive collaboration with the County of Santa Barbar and detailed analysis of their Zero Emission Vehicle Plan, we identified key business objectives—specifically, forecasting future charging capacity needs and optimizing station placement to meet the County's emission reduction goals.

- **Data Understanding**: We explored and analyzed two primary datasets (sessions and daily aggregates) from the PowerFlex reporting system, supplemented by vehicle population data from the California Energy Commission, to understand patterns, quality issues, and potential insights.

- **Data Preparation**: Rigorous cleaning, transformation, and feature engineering were performed, including standardizing date formats, handling outliers in charging duration data, and filtering for public charging sessions.

- **Modeling**: We developed multiple forecasting approaches, starting with baseline ARIMA models and advancing to STL (Seasonal and Trend decomposition using Loess) forecasting models to account for seasonality and external factors. Additionally, Decision Tree models were used to provide inference insight into questions the domain expert had about specific operational conditions. Lastly, future work planning includes neural network implementation for improved spike prediction (see ROADMAP.md file in this repository).

- **Evaluation**: Models are assessed using time-series cross-validation with metrics like RMSE, MAE, MAPE, and residual analysis to ensure forecasts accurately capture both current utilization patterns and future growth trajectories.

- **Deployment**: Results are being integrated directly into the County's decision-making process for their Zero Emission Vehicle Plan, with ongoing biweekly collaboration ensuring findings translate into actionable infrastructure planning. Furthermore, a [Streamlit dashboard application was created](https://zero-emission-vehicle-data-analyzer-csb.streamlit.app/) so that the county specialist can upload new file exports and get up-to-date forecast predictions, including warnings about energy usage spikes.

### Discovery and Continuous Engagement with County of Santa Barbara Domain Expert

- Beyond CRISP-DM, the project also leveraged the BizML framework described in [The AI Playbook](https://www.machinelearningkeynote.com/the-ai-playbook) by Eric Siegel. We applied the six core concepts of BizML to structure our collaboration with the County of Santa Barbara:

- **Establish the deployment goal**: We defined how machine learning would directly support CSB's Zero Emission Vehicle Plan. Our deployment goal was to create a Streamlit dashboard application that enables the County to anticipate charging infrastructure needs and make data-driven decisions about station placement and capacity planning. We established a ROADMAP with immediate goals and future improvements.
      
- **Establish the prediction goal**: During our biweekly discovery sessions between [Jerel Francisco](https://www.linkedin.com/in/jerel-francisco/), Zero-Emission Vehicle Specialist, and myself, we determined that forecasting daily energy demand (kWh delivered) would most effectively support the deployment goal. This prediction directly addresses CSB's need to understand future infrastructure requirements as EV adoption increases toward the 25% target.
      
- **Establish the evaluation metrics**: While the CRISP-DM section covers traditional model accuracy metrics, our BizML approach focused on defining success criteria for the entire deployment from an operational perspective. Working with the CSB representative, we established key performance indicators including:

**Infrastructure utilization improvement**: Measuring the percentage increase in charging station availability after policy recommendations are implemented.

**Planning efficiency**: Tracking the reduction in time required to make infrastructure expansion decisions using data-driven forecasts versus previous methods.

**Stakeholder confidence**: Assessing County officials' confidence in planning decisions through structured feedback sessions.

**Resource allocation impact**: Measuring how forecasted demand spikes correlate with actual peak periods, allowing the County to optimize resource allocation.

**Equity metrics**: Tracking whether charging infrastructure improvements reach underserved communities equitably.
   
These evaluation metrics shift the focus from model performance to business impact, ensuring that our technical solution translates into meaningful progress toward the Zero Emission Vehicle Plan's 25% EV adoption target.
      
- **Prepare the data**: We integrated three distinct datasets: session-level charging data (88,919 events), daily aggregates (1,827 days), and vehicle population statistics. Data preparation included filtering for public usage, standardizing temporal features, and addressing the substantial outliers discovered in the charging duration data. Jerel and I reviewed several different data sources, of which only a few were integrated into this report so far.
      
- **Train the model**: We developed progressively more sophisticated forecasting models, starting with baseline ARIMA models and advancing to STL forecasting to better capture seasonal patterns. Decision Tree models were also used to provide insight into specific operational questions from the domain expert.
      

- **Follow-through launch with stakeholders**: We engaged with Jerel Francisco and others in the County of Santa Barbara. Going forward we will train Jerel and others on how to use this report and the [dashboard application](https://zero-emission-vehicle-data-analyzer-csb.streamlit.app/) and establish a process for fine tunement and adjustments. IMPLEMENTATION documentation was created to provide continuous execution and improvement.

![SB-County-Zero-Emission-Vehicle-Plan-Demo-SQR](https://github.com/user-attachments/assets/63d12f93-2ca9-4e63-8173-f39556ff0fe4)
County of Santa Barbara - Zero Emission Vehicle Plan Demo Booth at Earth Day 2025 - Carlos Munoz Kampff (left) and Jerel Francisco (right)

### Phase 1: Data Preparation

#### Data Cleaning and Feature Engineering

- **Dataset Assessment**: The daily PowerFlex reporting data contained 1,827 rows and 22 columns, covering the period from January 2020 to December 2024.

- **Feature Removal**: Removed problematic features including:
  - `Max kW hour (kW)` due to systematic logging errors (consistently reporting 1am regardless of actual peak usage time)
  - `Max Utilization (%)`, `Faulted Stations`, and `Uptime (%)` were excluded from the main analysis as these were only consistently available after December 2023 (as confirmed by the CSB domain expert)

- **Date Formatting**: Converted the `Day` column to datetime format and set it as the index to create a proper time series dataset with daily frequency.

- **Partitioning**: Created a separate dataset (`df_reporting_2024`) for analyzing the newer metrics available only in 2024 data.

#### Missing Value Analysis and Imputation

- **Visualization of Missingness**: Generated comprehensive visualizations of missing value patterns across all features to identify data quality issues.

- **Targeted Imputation**: Applied mean imputation for features with minimal missing data:
  - `AVG session duration (minutes)`: Imputed with column mean
  - `AVG session idle (minutes)`: Imputed with column mean

- **Data Verification**: Verified completeness of energy delivery data (`Energy delivered (kWh)`), which was critical for the forecasting models.

![image](https://github.com/user-attachments/assets/7151f9f4-3781-4a0a-949f-34ad3ab043bd)

#### Outlier Identification and Analysis

- **Robust Detection Methods**: Applied Interquartile Range (IQR) method to identify outliers in the `Energy delivered (kWh)` feature:
  ```python
  Q1 = df_reporting['Energy delivered (kWh)'].quantile(0.25)
  Q3 = df_reporting['Energy delivered (kWh)'].quantile(0.75)
  IQR = Q3 - Q1
  lower_bound = Q1 - 1.5 * IQR
  upper_bound = Q3 + 1.5 * IQR
  ```

- **Outlier Assessment**: Identified outliers represented approximately 10% of the dataset, but closer examination revealed these were legitimate peak usage days rather than data errors.

- **Treatment Exploration**: Experimented with multiple outlier treatment methods to assess their impact on forecast accuracy:
  - Winsorization (capping values at IQR boundaries)
  - Median filtering (replacing outliers with values derived from rolling medians)
  - STL decomposition-based cleaning (replacing outliers in residual component)

- **Findings**: Determined that preserving original data without outlier treatment produced more accurate forecasts, suggesting that peaks in energy usage represent actual patterns relevant to capacity planning rather than noise.

#### Time Series Structuring

- **Time Series Conversion**: Transformed the dataset into a proper time series with daily frequency:
  ```python
  df_reporting_timeline = df_reporting.copy()
  df_reporting_timeline['Day'] = pd.to_datetime(df_reporting_timeline['Day'])
  df_reporting_timeline = df_reporting_timeline.set_index('Day')
  df_reporting_timeline = df_reporting_timeline.asfreq('D')
  ```

- **Stationarity Testing**: Applied the Augmented Dickey-Fuller (ADF) test to assess stationarity of the energy delivery time series:
  ```python
  result = adfuller(y_train)
  adf_statistic, p_value = result[0], result[1]
  ```
  
- **Differencing**: Applied first-order differencing to address non-stationarity identified in the ADF test (p-value > 0.05).

### Phase 2: Efficiency Analysis (Sessions Data)
- This analysis responds to the County's request to evaluate current infrastructure efficiency before expanding capacity. Key metrics to analyze include:

#### Idle Time Analysis

- At first, we observed some concerning signs of excessive idle states for the charging stations. When Jerel and I reviewed the initial statistical data, we were both taken aback by the fact that the average session duration was upwards of 900 minutes. After investigation, however, we were able to identify patterns and filter out CSB's fleet utilization. 
- Fortunately, the public charging stations only have excessive idleness 6% of the time. Nevertheless, this encourages further investigation and perhaps some policy changes for "peak hour" utilization of charging stations.
- The concern is that people park their cars for much longer than they need for EV charging thus reducing the availability of charging stations for those in actual need of them.
- As you can see in this graph idleness correlates very strongly with session duration.

  ![image](https://github.com/user-attachments/assets/f2652ca9-6dbb-483f-bd36-0490f8d48fc8)


#### Decision Tree Modeling as A Tool For Inference

- By exploring different correlation matrices and decision trees, Jerel and I had informative conversations about what factors affect the efficiency of the charging stations. 
- In this visualization, for example, you can see how the most predictive node when determining if a "charging" session will be 4 hours or longer is whether the driver is using the sites by the county jail. 

![image](https://github.com/user-attachments/assets/19290255-5584-422d-85e8-2dd9aee48308)

#### Visual Exploration with Mapping

- To explore the relationship between proximity to highways and other landmarks to features, we've produced 6 maps that can be reviewed in the /maps folder.
- This will be an area for future development as per the ROADMAP.md
![image](https://github.com/user-attachments/assets/e4380565-e663-4620-86dd-a789d51e733d)

### Phase 3: Time Series Forecasting (Days Data)

We developed a series of time series forecasting models to predict future EV charging demand, focusing on the daily energy delivered (kWh) metric. This analysis specifically targets data from 2022 onward, when meaningful energy usage patterns emerged in the County's charging infrastructure.

#### Time Series Decomposition and Stationarity Analysis

- **Augmented Dickey-Fuller Test**: Applied to assess stationarity of the energy delivery time series, revealing non-stationarity (p-value = 0.131) that required first-order differencing.

- **ACF and PACF Analysis**: Generated autocorrelation and partial autocorrelation plots for both original and differenced series:
  ```python
  fig, ax = plt.subplots(1, 4, figsize = (20, 5))
  plot_acf(y_train, ax = ax[0])
  plot_acf(y_train.diff().dropna(), ax = ax[1])
  plot_pacf(y_train.diff().dropna(), ax = ax[2], method = 'ywm')
  ```
  The analysis showed significant autocorrelation at multiple lags in the original series, with improvements after differencing.

- **Seasonal Decomposition**: Used STL (Seasonal and Trend decomposition using Loess) to separate the time series into trend, seasonal, and residual components:
  ```python
  result = seasonal_decompose(y_train, model='additive', period=360)
  result.plot()
  ```

#### Model Development and Selection

- **Initial ARIMA Model**: Implemented a baseline ARIMA(1,1,0) model based on ACF and PACF analysis.
  ```python
  model = ARIMA(y_train, order=(1, 1, 0))
  model_fit = model.fit()
  ```

- **STL-ARIMA Hybrid Approach**: Developed a more sophisticated model combining STL decomposition with ARIMA modeling:
  ```python
  stlf = STLForecast(y_train, ARIMA, model_kwargs={'order':(1, 1, 0), 'trend':"t"}, period=30)
  stlf_results = stlf.fit()
  ```

- **Seasonality Parameter Tuning**: Systematically evaluated different seasonality periods (7, 30, 90, 180, 360 days) to identify optimal patterns, with 30-day seasonality producing the most accurate forecasts:
  ```python
  # Best STL period: 30 with RMSE: 482.44
  ```

- **ARIMA Parameter Optimization**: Tested various ARIMA specifications (p,d,q) including (1,1,0), (1,1,1), (2,1,0), (2,1,1), and (1,1,2), with the simpler ARIMA(1,1,0) model performing well.

#### Model Validation and Performance

- **Train-Test Split**: Implemented a 70/30 time series split for model validation:
  ```python
  split_point = int(len(energy_df) * 0.7)
  y_train = energy_df.iloc[:split_point]
  y_test = energy_df.iloc[split_point:]
  ```

- **Comprehensive Error Metrics**: Evaluated model performance using multiple metrics:
  ```python
  mse_stl = mean_squared_error(y_test, forecast)
  rmse_stl = np.sqrt(mse_stl)
  mae_stl = mean_absolute_error(y_test, forecast)
  mape_stl = np.mean(np.abs((y_test - forecast) / y_test)) * 100
  ```
  
- **Diagnostic Visualization**: Created forecast vs. actual plots to visually assess model performance and identify potential areas for improvement.

- **Model Comparison**: The STL-ARIMA model with 30-day seasonality outperformed the baseline ARIMA model, demonstrating its effectiveness at capturing both trend and seasonal patterns.

#### Long-term Forecasting to 2030

- **Growth Factor Integration**: Incorporated two different growth scenarios based on:
  1. **Zero-Emission Vehicle Plan Growth Rate**: Calculated from the CSB's plan to increase from 6,000 to 81,250 EVs by 2030
  2. **Observed Historical Growth Rate**: Derived from California Energy Commission data (1.3698 annual growth factor)

- **Multi-Scenario Forecasting**: Generated three distinct forecasts:
  ```python
  # Base forecast without growth scaling
  base_forecast = stlf_results.forecast(forecast_horizon)
  
  # Zero-Emission Vehicle Plan forecast
  projected_forecast = base_forecast * projected_multipliers
  
  # Historical trend forecast
  observed_forecast = base_forecast * observed_multipliers
  ```

- **Scenario Analysis Visualization**: Created comparative visualization of different growth scenarios, with annotated reference points at key years:
  ```python
  plt.figure(figsize=(15, 8))
  plt.plot(energy_df.index, energy_df, label='Historical Data', color='black', linewidth=2)
  plt.plot(base_forecast.index, base_forecast, label='Base Forecast (No Growth Factor)', 
         color='blue', alpha=0.6, linestyle='--')
  plt.plot(projected_forecast.index, projected_forecast, 
         label=f'Zero-Emission Vehicle Plan Forecast (Growth Factor: {annual_growth_factor:.2f})', 
         color='green', linewidth=2)
  plt.plot(observed_forecast.index, observed_forecast, 
         label=f'Historical Trend Forecast (Growth Factor: {observed_growth_factor:.2f})', 
         color='red', linewidth=2)
  ```

- **Final Year Analysis**: Quantified the expected energy demand for the final forecast year (2030):
  ```python
  print("\nSummary of final year forecasts (2030):")
  print(f"Base forecast total: {base_forecast[start_date_of_final_year:].sum():.0f} kWh")
  print(f"ZEV Plan forecast total: {projected_forecast[start_date_of_final_year:].sum():.0f} kWh")
  print(f"Historical trend forecast total: {observed_forecast[start_date_of_final_year:].sum():.0f} kWh")
  ```

### Expected Outcomes

#### Infrastructure Efficiency Assessment

- Quantification of current utilization rates.
- Identification of optimization opportunities.
- Recommendations for improved efficiency.

#### Capacity Forecasting Model

- Time-series analysis based on historical data to estimate daily energy delivery requirements through 2030.
- Three forecast scenarios: baseline growth, ZEV mandate alignment, and historical trend extrapolation.
- Current limitations include uncertainty in long-term adoption patterns and limited geographic granularity.
- Provides directional insights to inform infrastructure planning rather than precise capacity requirements.

#### Policy Recommendations

- Data-informed strategies for optimizing existing charging infrastructure utilization.
- Prioritization criteria for future infrastructure investments based on actual usage patterns.
- Recommended metrics and KPIs for measuring ongoing performance against climate goals.
- Guidelines for balancing immediate operational needs with long-term strategic objectives.

### Alignment with Climate Action Plan Goals
This analysis contributes to the County's 2030 Climate Action Plan Zero Emission Mobility Goals through:

- Quantifying current infrastructure utilization to establish a baseline for measuring progress toward the 25% passenger EV ownership goal.
- Identifying potential bottlenecks and optimization opportunities to support the transition toward 15% commercial EV use.
- Providing data-driven insights to inform decisions about the placement and specifications of future public EV chargers.
- Creating a measurement framework that enables regular assessment of infrastructure performance against adoption targets.

## Results

### STL-ARIMA Model with 30-Day Seasonality

Our final model implements a hybrid STL-ARIMA approach with 30-day seasonality, which has significantly improved forecasting accuracy compared to earlier iterations. This sophisticated model:

1. **Decomposes the time series** using Seasonal and Trend decomposition with Loess (STL), effectively separating the data into seasonal, trend, and residual components.
2. **Applies ARIMA modeling** to the residual component to capture remaining patterns after seasonality and trend have been accounted for.
3. **Reintroduces the 30-day seasonality pattern** based on detailed analysis of the historical charging data, which revealed monthly utilization cycles aligned with county employee work patterns and public facility usage.

As shown in the forecast visualization, the model successfully:

1. Tracks the rising trend in energy delivered (kWh), aligning with the accelerating EV adoption rates in Santa Barbara County.
2. Captures both weekly and monthly seasonal fluctuations in charging patterns.
3. Provides predictions that follow the general volatility pattern of the actual test data, including appropriate confidence intervals.

### Performance Metrics

The model demonstrates strong performance with the following metrics:
- **RMSE (Root Mean Square Error)**: 482.44 kWh
- **MAE (Mean Absolute Error)**: 394.62 kWh
- **MAPE (Mean Absolute Percentage Error)**: 33.43%

These metrics represent a substantial improvement over previous models, with a 27% reduction in RMSE compared to our baseline ARIMA model. While there remains opportunity for enhancement, particularly in capturing extreme peak values during high-demand periods, the forecast provides statistically robust insights for infrastructure planning.

The model now serves as a reliable foundation for the County's short and medium-term planning needs, enabling projection of both "natural" growth trends and the "aspirational" upward trajectory targets outlined in the Zero Emission Vehicle Plan.

![image](https://github.com/user-attachments/assets/f09ba3df-0102-4b99-b1dd-283ee2e9deda)

# Scenario Projections to 2030 and Beyond

## Forecasting Methodology
While our STL-ARIMA model provides reliable short-term forecasting (3–6 months), long-term infrastructure planning requires scenario-based projections that incorporate broader EV adoption trends. Our approach combines statistical time series analysis with growth factors derived from multiple authoritative sources.

## Hybrid Forecasting Approach
We developed a hybrid forecasting methodology that:
1. Uses STL-ARIMA for baseline forecasting with seasonal patterns and underlying trends.
2. Applies various growth factors to model different EV adoption scenarios.
3. Projects these scenarios through 2030 to support strategic infrastructure planning.

This approach enables both operational forecasting and strategic capacity planning—giving Santa Barbara County a way to manage near-term fluctuations while preparing for long-term infrastructure needs.

## Three Key Scenarios

Our analysis modeled three distinct scenarios for daily energy demand by 2030:

| Scenario | Daily Energy (2030) | Growth Factor | Data Source |
|----------|---------------------|---------------|-------------|
| Conservative | 2,929 kWh | 1.0862 | Empirical charging station usage trends |
| Historical Trend | 14,111 kWh | 1.3698 | California Energy Commission vehicle adoption data (2010-2023) |
| ZEV Plan Target | 39,601 kWh | 1.5784 | California Zero-Emission Vehicle plan targets |

## Key Insights

The substantial variance between scenarios highlights the importance of flexible infrastructure planning:

- **Conservative Scenario**: Based solely on charging station usage patterns, this represents minimal growth. While statistically sound, it likely underestimates future demand by not accounting for accelerating EV adoption.

- **Historical Trend Scenario**: Derived from California Energy Commission data spanning 2010-2023, this scenario applies the observed annual growth factor of 1.3698 (36.98% annual growth). The longer timeframe captures established adoption patterns and provides a more realistic projection.

- **ZEV Plan Target Scenario**: Aligned with California's Zero-Emission Vehicle targets, this scenario represents the policy-driven goal of reaching 25% EV penetration in Santa Barbara County by 2030. This requires the most aggressive infrastructure expansion.

## Planning Implications

- **Short-term (≤6 months)**: Use the STL-ARIMA forecast to optimize daily operations and identify immediate peak usage remediation needs.

- **Medium-term (6 months to 2 years)**: Plan infrastructure upgrades based on the Historical Trend scenario while monitoring actual adoption rates.

- **Long-term (3+ years)**: Design grid capacity to accommodate flexible scaling between the Historical Trend and ZEV Plan Target scenarios, with regular reassessment as adoption patterns evolve.

This multi-scenario approach provides Santa Barbara County with a robust framework for EV infrastructure planning that balances immediate operational needs with strategic long-term capacity development.

### Three Scenario Projections Based on the PowerFlex Data Modeling (Base Forecast), the Energy Commission Data Trends and the Zero-Emission Vehicle Plan Targets

![image](https://github.com/user-attachments/assets/188839e2-f587-407c-bd5d-8ec6280b93de)

### For Reference: This is the Historical EV Adoption Data From California Energy Commission for CSB

![image](https://github.com/user-attachments/assets/8d612815-f260-48f8-a3e4-b5b0620df916)

This data and visualization is described in the data-analysis-vehicle-population.ipynb notebook.

## Future Model Enhancements

Based on our analysis and the current model performance, we've identified several promising avenues for further improvement:

### Advanced Time Series Techniques
- **Optimize differencing parameters** in the ARIMA component to better capture the non-stationary aspects of the data
- **Explore RNN forecast modeling** (Recursive Neural Network) to better handle the inherent volatility in charging demand patterns. Such a model will include a larger set of features to create more robust predictions.
- **Implement ensemble methods** combining multiple forecasting models to improve robustness across different time horizons

### Data Preprocessing Refinements
- **Develop a robust outlier detection and treatment methodology** to address the significant outliers identified in the [data-analysis-days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-days.ipynb) notebook
- **Conduct causal factor analysis** to understand the operational significance of these outliers and their relationship to special events or system anomalies
- **Create specialized holiday and event features** to account for predictable demand pattern disruptions

### Validation and Integration
- **Extend cross-validation procedures** to ensure model stability across different seasonal periods
- **Develop automated retraining pipelines** to incorporate new data as it becomes available
- **Integrate forecasts with the County's infrastructure planning tools** to translate predictions directly into actionable capacity planning recommendations

These enhancements will be prioritized based on the County's immediate planning needs and available resources.

### Additional Forecasting Targets
- Forecast other features such as "Started Sessions" in the "Days" dataset since it might be more stationary
  
## Recommendations and Implementation

- Please review the [IMPLEMENTATION](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/IMPLEMENTATION.md) file for more detailed insights and proposals. 
- Additionally, there is a [ROADMAP](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/ROADMAP.md) file that provides guidance for the next steps of the collaboration with the County of Santa Barbara. 
- The [Streamlit dashboard application](https://zero-emission-vehicle-data-analyzer-csb.streamlit.app/) serves as the primary tool for transportation department staff to interact with the EV charging data and forecasting models, providing valuable insights to support the Zero Emission Vehicle Plan implementation. This dashboard uses OpenAI-powered AI analysis (with fallback support) to automatically highlight significant trends and anomalies in the charging data, while also enabling staff to generate forecasts that directly support capacity planning, policy optimization, and progress tracking toward climate goals. 

### The data revealed two key actionable insights:
1. The Zero-Emission Vehicle Plan sets an aggressive target that exceeds current trends revealed by the data. If that target is to be reached, 39,601 kWh of daily electricity usage would be needed according to our model. More comprehensive evaluation is necessary to create robust predictions and to understand potential energy spikes. At minimum, consultation with an energy capacity expert is recommended.

2. The civilian fleet is engaging in excessively long "idling" sessions. This pattern was initially masked by the County's BEV fleet, since county cars are parked for days on charging stations used exclusively by the county. Our data filtering revealed that while public utilization is mostly efficient, there are specific areas for improvement. Although only 6% of sessions last 4 hours or longer (as shown in the data-analysis-sessions notebook), each such vehicle occupies valuable charging station space. For perspective, 8 cars could each charge for 30 minutes during a 4-hour window. This indicates significant opportunity to increase capacity through smart policy changes.

## Outline of project

- PRIMARY NOTEBOOK FOR MODEL DEVELOPMENT: [data-analysis-days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-days.ipynb)
- EXPLORATORY NOTEBOOK: [data-analysis-sessions](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-sessions.ipynb)
- EXPLORATORY NOTEBOOK: [data-analysis-vehicle-population](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-vehicle-population.ipynb)
- DEPLOYED MODEL APPLICATION: [dashboard-app](https://github.com/elmunoz42/sbcc-ev-charging-stations/tree/main/dashboard-app)
- [ROADMAP](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/ROADMAP.md)
- [IMPLEMENTATION](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/IMPLEMENTATION.md)

## Additional Deliverables
- The data visualizations are available for download in the "Images" folder.
- Certain report tables have been added to this project as CSV files. For example, the statistical analysis of Type 2 (Webasto) and Type 3 (Delta) charging stations:
     - https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/webasto_dx_statistics.csv
     - https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/delta_statistics.csv
- The maps folder has 6 maps of the County's public charging stations each focusing on a different feature's statistics:
     - https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/maps/4_plus_hour_session_map.html
     - https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/maps/Charging_duration_minutes_map.html
     - https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/maps/Cost_to_driver_map.html
     - https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/maps/Cost_to_site_map.html
     - https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/maps/Session_duration_minutes_map.html
     - https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/maps/kWh_delivered_map.html


# Bonus Section - RNN Forecasting Model

In addition to the STL Arima forecasting model I also tested an RNN forecasting model. Currently there wasn't enough data for this to result in a significant improvement. This much more complex neural network model only improves the error rate by 0.6% in RMSE compared to our production model. While further exploration with different neural network configurations could be potentially beneficial, the main inflection point will simply be having more meaningful data. The County of Santa Barbara only has 2 years of meaningful charging data. I imagine that in a year from now the RNN model will do much better and will easily outperform the STL-Arima baseline model. At this time however it is more prudent to keep the deployed model as is since it is much easier to understand and maintain. 

## IMPORTANT NOTE:

Please note that the RNN model in the notebook requires a graphic card to compute. I used the Google Colab Pro A100. The model might fail if your kernel is running on a regular CPU. Below is a link to the Google Colab Notebook, a paid upgrade might be needed to fit the model. Alternatively, running the notebook on a local Anaconda server with a NVidia card can also work.

[Google Colab Notebook](https://colab.research.google.com/drive/1wcdJn2BWfyFMBqbq5qLlqKagtWWZ4doq?usp=sharing)

## RNN Model Structure Overview

This creates a stacked LSTM model with the following layers:

### Layer 1: First LSTM (50 units)
`pythonLSTM(50, return_sequences=True, input_shape=input_shape)`

50 units: Creates 50 LSTM memory cells that can learn different temporal patterns
return_sequences=True: This is key - it outputs the full sequence rather than just the final output, allowing the next LSTM layer to see the entire processed sequence
input_shape: Expects 3D input (batch_size, time_steps, features)

### Layer 2: Dropout (20%)
`pythonDropout(dropout_rate)`

Randomly sets 20% of neurons to zero during training
Prevents overfitting by forcing the model not to rely too heavily on specific neurons
Only active during training, not prediction

### Layer 3: Second LSTM (50 units)
`pythonLSTM(50, return_sequences=False)`

Another 50 LSTM units to capture more complex patterns
return_sequences=False: Only outputs the final time step's result (not the full sequence)
This creates the transition from sequence processing to final prediction

### Layer 4: Another Dropout
Same 20% dropout for regularization
Layer 5: Dense Layer (25 units)
pythonDense(25, activation='relu')

Fully connected layer with 25 neurons
ReLU activation: Helps with non-linear pattern recognition
Acts as a "feature combiner" before final prediction

### Layer 6: Output Layer (1 unit)
`pythonDense(1, activation='linear')`

Single output neuron for energy demand prediction
Linear activation: No transformation, direct numeric output

### Contact and Further Information

https://carlosmunozkampff.com/contact 
https://www.linkedin.com/in/carlos-munoz-kampff/
