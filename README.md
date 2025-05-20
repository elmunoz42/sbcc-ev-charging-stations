# How Can the County of Santa Barbara's Electric Vehicle Charging Infrastructure Data Advance the Implementation of the Zero Emission Vehicle Plan? 

## Executive Summary

This ongoing research project analyzes historical electric vehicle (EV) charging data to support the County of Santa Barbara's Zero Emission Vehicle Plan. With transportation accounting for 48% of the County's greenhouse gas emissions and an ambitious goal to reduce community-wide emissions by 50% by 2030, optimizing EV charging infrastructure is critical to achieving climate targets.
The study examines four years (2020-2024) of charging station utilization data collected from the County's PowerFlex reporting system. Two primary datasets were analyzed: a session-level dataset containing 88,919 individual charging events and a day-level dataset with 1,827 days of aggregated metrics.

### Key findings include:

- **Growth in Energy Demand**: PowerFlex time series data reveals a consistent upward trend in kilowatt-hours of energy delivered through charging stations, with identifiable seasonality patterns that have been captured in our forecasting models.
  
- **Accelerating EV Adoption**: California Energy Department data demonstrates an exponential increase in battery electric vehicles, confirming the need for Santa Barbara County's ambitious infrastructure expansion plans.
  
- **Optimization Opportunities**: Decision tree analysis identified efficiency improvements that could complement new station construction—specifically, targeting the 6% of charging sessions with excessive idle times through policy adjustments could significantly increase existing infrastructure capacity.

## Research Question

How can historical electric vehicle (EV) charging station utilization data be used to forecast future charging capacity needs and optimize charging station placement in the County of Santa Barbara to help meet the "Zero Emission Vehicle Plan" goals?

## Rationale

The County of Santa Barbara (CSB) has ambitious greenhouse gas emission goals. The following excerpt is from a document my CSB liaison at the transportation department Jerel Francisco is working on. The document is already in a public draft format and available on the [CSB's transportation department website](https://www.countyofsb.org/3218/Transportation).

### County of Santa Barbara Zero Emission Vehicle Plan (Public Draft) - May 2025 - Transportation Department

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

*Response strategy:* By training a forecasting model, we will be able to get a sense of the rapid oscillations and seasonal peaks and troughs we are to expect. E.g., tourist seasons, work commute rush, etc. One important consideration is that we will need to forecast the amount of total passenger cars the CSB will have by then compared to today to accurately predict the pertinent metrics for the 25% we are hoping will be EVs. In other words: If the amount of EVs today requires a charging grid with a certain capacity, how much will the future amount of EVs that we are hoping for require?

2) Are there ways to optimize the grid to meet more energy output demand by modifying public utilization policies?

*Response strategy:* We will review the sessions data with visualizations, coefficient matrices, and decision tree modeling and inference. This will enable a much deeper understanding of the factors that are at play and allow for effective policy recommendations. E.g., reducing the idling time allowance during peak hours from 4 to 2 hours before a penalty charge. Please note that any such policy change will need to thoroughly consider not just logistic impacts but also accessibility impact on the CSB's citizens, especially marginalized groups, as this is an imperative clearly stated in the "Zero Emission Vehicle Plan".

*Summary:* This capstone research paper will work to address these 2 items in turn. Additionally, we have already been providing CSB value in performing statistical analysis and visualizations for data that had never before been thoroughly explored. Our hope is that the timing coincides and findings from this report can actually inform CSB's "Zero Emission Vehicle Plan" official report that is being actively worked on by Jerel Francisco and his colleagues. Furthermore, there is a ROADMAP document with future improvements we plan to deploy in the next few months.
   
## Data Sources

CSB's charging stations are integrated with a PowerFlex reporting system with up-to-date utilization metrics. The historical charging station utilization data includes session times, idle times, and energy consumption. Jerel Francisco exported the data from January 1st 2020 to December 31st 2024 for two types of data exports:
- [Sessions](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data/SB-County-County-Public-Portfolio-stations-report-01_01_20-12_31_24.csv):
      - This data has 88,919 rows and 30 columns. Each row represents a unique charging session, with information about the charging site, session duration, energy usage etc.
      - The samples include public and CSB fleet vehicle utilization. Since Jerel Francisco had particular interest in the public utilization of the resources, we filter out for public usage only early on in our analysis of this dataset.
- [Days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data/SB-County-County%20Public%20reporting%202020-01-01_2024-12-31.csv):
      - This data has 1,827 rows and 22 columns. Each row represents a day in the 4-year period with data aggregated from all charging sites with information about metric averages.
- [Cars](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-vehicle-population.ipynb):
      - This is data from the California Energy department [website](https://www.energy.ca.gov/data-reports/energy-almanac/zero-emission-vehicle-and-infrastructure-statistics-collection/light). It tracks the light-duty vehicle population in California. 

For a breakdown of all the features please review the respective feature catalogues:
- [Sessions](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/sessions-feature-catalogue.md)
- [Days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/days-feature-catalogue.md)

## Methodology

### CRISP-DM Framework

The project follows the Cross-Industry Standard Process for Data Mining (CRISP-DM) framework to ensure a structured and comprehensive approach:

- **Business Understanding**: Through extensive collaboration with the County of Santa Barbara's transportation department and detailed analysis of their Zero Emission Vehicle Plan, we identified key business objectives—specifically, forecasting future charging capacity needs and optimizing station placement to meet the County's emission reduction goals.

- **Data Understanding**: We explored and analyzed two primary datasets (sessions and daily aggregates) from the PowerFlex reporting system, supplemented by vehicle population data from the California Energy Department, to understand patterns, quality issues, and potential insights.

- **Data Preparation**: Rigorous cleaning, transformation, and feature engineering was performed, including standardizing date formats, handling outliers in charging duration data, and filtering for public charging sessions.

- **Modeling**: We developed multiple forecasting approaches, starting with baseline ARIMA models and advancing to STL (Seasonal and Trend decomposition using Loess) forecasting models to account for seasonality and external factors. Additionally, Decision Tree models were used to provide inference insight into questions the domain expert had about specific operational conditions. Lastly, future work planning includes neural network implementation for improved spike prediction (see ROADMAP.md file in this repository).

- **Evaluation**: Models are assessed using time-series cross-validation with metrics like RMSE, MAE, MAPE, and residual analysis to ensure forecasts accurately capture both current utilization patterns and future growth trajectories.

- **Deployment**: Results are being integrated directly into the County's decision-making process for their Zero Emission Vehicle Plan, with ongoing biweekly collaboration ensuring findings translate into actionable infrastructure planning. Furthermore, a Streamlit dashboard application was created so that the county specialist can upload new file exports and get up-to-date forecast predictions, including warnings about energy usage spikes.

### Discovery and Continuous Engagement with County of Santa Barbara Domain Expert

- Beyond CRISP-DM, the project also leveraged the BizML framework described in [The AI Playbook](https://www.machinelearningkeynote.com/the-ai-playbook) by Eric Siegel. We applied the six core concepts of BizML to structure our collaboration with the County of Santa Barbara:

      1. **Establish the deployment goal**: We defined how machine learning would directly support CSB's Zero Emission Vehicle Plan. Our deployment goal was to create a Streamlit dashboard application that enables the County to anticipate charging infrastructure needs and make data-driven decisions about station placement and capacity planning. We established a ROADMAP with immediate goals and future improvements.
      
      2. **Establish the prediction goal**: During our biweekly discovery sessions with [Jerel Francisco](https://www.linkedin.com/in/jerel-francisco/), Zero-Emission Vehicle Specialist and I, we determined that forecasting daily energy demand (kWh delivered) would most effectively support the deployment goal. This prediction directly addresses CSB's need to understand future infrastructure requirements as EV adoption increases toward the 25% target.
      
      3. **Establish the evaluation metrics**: We selected RMSE, MAE, and MAPE as our primary metrics, with special emphasis on model performance during demand spikes, as these periods are critical for infrastructure planning. After consultation with Jerel, we established that forecasts needed to capture both the general trend and seasonal fluctuations (e.g., tourist seasons, commute patterns).
      
      4. **Prepare the data**: We integrated three distinct datasets: session-level charging data (88,919 events), daily aggregates (1,827 days), and vehicle population statistics. Data preparation included filtering for public usage, standardizing temporal features, and addressing the substantial outliers discovered in the charging duration data.
      
      5. **Train the model**: We developed progressively more sophisticated forecasting models, starting with baseline ARIMA models and advancing to STL forecasting to better capture seasonal patterns. Decision Tree models were also used to provide insight into specific operational questions from the domain expert.
      
      6. **Deploy the model**: The forecasting models were integrated into a Streamlit dashboard application that allows CSB staff to upload new PowerFlex data exports and receive updated predictions, including alerts for anticipated demand spikes. This deployment directly supports the County's infrastructure planning process.

![SB-County-Zero-Emission-Vehicle-Plan-Demo-SQR](https://github.com/user-attachments/assets/63d12f93-2ca9-4e63-8173-f39556ff0fe4)
County of Santa Barbara - Zero Emission Vehicle Plan Demo Booth at Earth Day 2025 - Carlos Munoz Kampff (left) and Jerel Francisco (right)

### Phase 1: Data Preparation

#### Data Cleaning

- Remove duplicate records (if any)
- Standardize date/time formats
- Convert data types as needed (e.g., string dates to datetime objects)

#### Outlier Identification and Handling

- Use statistical methods (z-scores, IQR) to identify anomalous values
- Evaluate contextual validity of outliers (e.g., unusually long sessions)
- Apply appropriate treatment (removal, capping, or flagging)


#### Missing Value Imputation

- Assess patterns of missingness in both datasets
- Apply appropriate imputation techniques based on data characteristics.

### Phase 2: Efficiency Analysis (Sessions Data)
- This analysis responds to the County's request to evaluate current infrastructure efficiency before expanding capacity. Key metrics to analyze include:

#### Idle Time Analysis

- At first, we had seen some concerning signs of excessive idle states for the charging stations. When Jerel and I reviewed the initial statistical data, we were both taken aback by the fact that the average session duration was upwards of 900 minutes. After some investigation though, we were able to identify some patterns and filter out CSB's fleet utilization. 
- Fortunately, the public charging stations only have excessive idleness 6% of the time. Nevertheless, this is encouraging further investigation and perhaps some policy changes for "peak hour" utilization of charging stations.
- The concern is that people park their cars for much longer than they need for EV charging thus reducing the availability of charging stations for those in actual need of them.

#### Utilization Pattern Analysis

- Peak usage periods vs. low-demand periods
- Geographic distribution of high/low utilization
- Correlation between station type and utilization rate

#### Charging Behavior Analysis

- Distribution of session durations
- Energy consumption patterns
- Relationship between charging duration and energy delivered

### Phase 3: Time Series Forecasting (Days Data)
A SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous variables) model will be developed to forecast future charging demand, focusing primarily on daily energy delivered (kWh).

#### Time Series Decomposition
- Adfuller test
- Trend component
- Seasonal components (daily, weekly, monthly patterns)
- Irregular components

#### Model Development

- Parameter selection (p, d, q, P, D, Q)
- Inclusion of seasonal components
- Integration of exogenous variables:

    - EV adoption rates in Santa Barbara County
    - Economic indicators
    - Policy changes


#### Model Validation

- Cross-validation using time series split
- Error metrics (RMSE, MAE, MAPE)
- Residual analysis

#### 2030 Forecasting

- Projection of daily kWh delivered through 2030
- Confidence intervals
- Scenario analysis based on different EV adoption rates

### Expected Outcomes

#### Infrastructure Efficiency Assessment

- Quantification of current utilization rates
- Identification of optimization opportunities
- Recommendations for improved efficiency

#### Capacity Forecasting Model

- Projected daily and annual energy delivery requirements through 2030
- Estimated number of additional charging stations needed
- Geographic distribution recommendations

#### Policy Recommendations

- Evidence-based strategies to support the County's climate goals
- Prioritization framework for infrastructure investments
- Monitoring approach for ongoing performance assessment

### Alignment with Climate Action Plan Goals
This analysis directly supports the County's 2030 Climate Action Plan Zero Emission Mobility Goals by:

- Providing data-driven projections to support the 25% passenger EV ownership goal
- Identifying infrastructure needs for the 15% commercial EV use goal
- Informing strategic placement of the 375 publicly available EV chargers
- Establishing a framework for ongoing monitoring and optimization

## Results

The initial baseline forecast model fails to represent the upward trajectory of the test data. This might be improved using the SARIMAX model instead of ARIMA to account for seasonality, natural trends and other factors. Furthermore, the data might need a higher differencing value so that it is stationary, cross validation will be employed to fine tune such hyperparameters. One additional consideration, as previously discussed, besides the "natural" growth trend we will also compute the "aspirational" upward trend that is the target of the Zero Emission Vehicle Plan. So a few different models will need to be calculated and reviewed to accomplish our objectives.

![image](https://github.com/user-attachments/assets/8ae1b73d-754f-457f-85b1-587ab74e563c)

## Next steps

- Investigate different values for differencing.
- Add seasonality and trends to the model.
- In my searches, a recommendation for the GARCH model was mentioned to better handle the volatility of the data.
- Investigate how outliers and data volatility might be affecting the predictions. In Fig2_C in the [data-analysis-days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-days.ipynb) notebook there are significant outliers that need to be accounted for to improve the preditions. This process needs to be reviewed carefully though because we need to understand the importance of the outliers and the impact they have on the EV charging infrastructure.
  ![image](https://github.com/user-attachments/assets/cdabc2ed-4154-4071-83a2-50c2a24e2994)
- Forecast other features such as "Started Sessions" in the "Days" dataset since it might be more stationary.
  
## Outline of project

- [data-analysis-sessions](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-sessions.ipynb)
- [data-analysis-days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-days.ipynb)
- [dashboard-app](https://github.com/elmunoz42/sbcc-ev-charging-stations/tree/main/dashboard-app)
- [ROADMAP](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/ROADMAP.md)

## Additional deliverables
- The data visualizations are available for download in the "Images" folder.
- Certain report tables will have been added to this project as CSV files. For example the statistical analysis of Type 2 (Webasto) and Type 3 (Delta) charging stations.
     - https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/webasto_dx_statistics.csv
     - https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/delta_statistics.csv

### Contact and Further Information

https://carlosmunozkampff.com/contact 
https://www.linkedin.com/in/carlos-munoz-kampff/
