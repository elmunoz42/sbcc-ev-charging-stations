## How Can the County of Santa Barbara's Electric Vehicle Charging Infrastructure Data Advance the Implementation of the Zero Emission Vehicle Plan? 

### Executive Summary

### Research Question

How can historical electric vehicle (EV) charging station utilization data be used to forecast future charging capacity needs and optimize charging station placement in the County of Santa Barbara to help meet the "Zero Emission Vehicle Plan" goals?

### Rationale

The County of Santa Barbara (CSB) has ambitious greenhouse gas emission goals. The following excerpt is from a document my CSB liaison at the transportation department Jerel Francisco is working on. The document is already in a public draft format and available on the [CSB's transportation department website](https://www.countyofsb.org/3218/Transportation).

#### County of Santa Barbara Zero Emission Vehicle Plan (Public Draft) - May 2025 - Transportation Department

##### URL: https://cosantabarbara.app.box.com/s/uyds828nxptcrtsjbqssyiu4rpps5odr
##### Excerpt:

"The County has been a leader in climate action, taking steps to reduce greenhouse gas (GHG) emissions and prepare for climate impacts. The 2030 Climate Action Plan (CAP) has a target to reduce community-wide emissions 50% by 2030 (below 2018 levels). On-road vehicle transportation accounts for 48% of the County's GHG emissions¹. As of 2022, zero emission vehicles (ZEV) make up less than 2% of all vehicles on the road in Santa Barbara County.

To meet State and local emission reduction targets, the CAP includes the following goals to reduce transportation-related emissions:

##### Table 1. 2030 Climate Action Plan Zero Emission Mobility Goals

| CAP Goal | 2030 Goal | 2045 Goal |
|----------|-----------|-----------|
| Increase passenger electric vehicle ownership | 25% | 90% |
| Increase commercial electric vehicle use | 15% | 75% |
| Install at least 375 publicly available electric vehicle chargers | 375 | NA |
| Decarbonize off-road equipment | 21% | 38% |
| Increase bike-mode share | 1% | 5% |

ZEV planning and implementation transects nearly all County operations and community functions, from fleet vehicles, building regulations, infrastructure, parking and energy management. It will require action from both internal County Departments and local community and municipal partners to help implement the Actions (page 31) identified in this plan."

### Data Sources

CSB's charging stations are integrated with a PowerFlex reporting system with up-to-date utilization metrics. The historical charging station utilization data includes session times, idle times, and energy consumption. Jerel Francisco exported the data from January 1st 2020 to December 31st 2024 for two types of data exports:
- [Sessions](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data/SB-County-County-Public-Portfolio-stations-report-01_01_20-12_31_24.csv):
      - This data has 88,919 rows and 30 columns. Each row represents a unique charging session, with information about the charging site, session duration, energy usage etc.
      - The samples include public and CSB fleet vehicle utilization. Since Jerel Francisco had particular interest in the public utilization of the resources, we filter out for public usage only early on in our analysis of this dataset.
- [Days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data/SB-County-County%20Public%20reporting%202020-01-01_2024-12-31.csv):
      - This data has 1,827 rows and 22 columns. Each row represents a day in the 4-year period with data aggregated from all charging sites with information about metric averages.

For a breakdown of all the features please review the respective feature catalogues:
- [Sessions](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/sessions-feature-catalogue.md)
- [Days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/days-feature-catalogue.md)

### Methodology

#### Discovery and Continuous Engagement with County of Santa Barbara Domain Expert

The project began with a 1-hour discovery meeting. We discussed the CSB's objectives, plans and pain points. We went over their different data sources and additional resources we could merge into our research effort.

Since then Jerel Francisco and I have met for 1 hour every two weeks and have already had 4 meetings thus far. Some of the visualizations and statistical analysis in the Jupyter Notebooks are direct answers to questions he had about the data since it has not been previously analyzed. 

#### Phase 1: Data Preparation

##### Data Cleaning

Remove duplicate records (if any)
Standardize date/time formats
Convert data types as needed (e.g., string dates to datetime objects)


##### Outlier Identification and Handling

Use statistical methods (z-scores, IQR) to identify anomalous values
Evaluate contextual validity of outliers (e.g., unusually long sessions)
Apply appropriate treatment (removal, capping, or flagging)


##### Missing Value Imputation

Assess patterns of missingness in both datasets
Apply appropriate imputation techniques based on data characteristics.

#### Phase 2: Efficiency Analysis (Sessions Data)
This analysis responds to the County's request to evaluate current infrastructure efficiency before expanding capacity. Key metrics to analyze include:

##### Idle Time Analysis

Initial finding: Public charging stations show only 6% idle time
Further segmentation by:

Time of day
Day of week
Location
User type (if available)

##### Utilization Pattern Analysis

Peak usage periods vs. low-demand periods
Geographic distribution of high/low utilization
Correlation between station type and utilization rate

##### Charging Behavior Analysis

Distribution of session durations
Energy consumption patterns
Relationship between charging duration and energy delivered

#### Phase 3: Time Series Forecasting (Days Data)
A SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous variables) model will be developed to forecast future charging demand, focusing primarily on daily energy delivered (kWh).

##### Time Series Decomposition

Trend component
Seasonal components (daily, weekly, monthly patterns)
Irregular components

##### Model Development

Parameter selection (p, d, q, P, D, Q)
Inclusion of seasonal components
Integration of exogenous variables:

EV adoption rates in Santa Barbara County
Economic indicators
Policy changes


##### Model Validation

Cross-validation using time series split
Error metrics (RMSE, MAE, MAPE)
Residual analysis

##### 2030 Forecasting

Projection of daily kWh delivered through 2030
Confidence intervals
Scenario analysis based on different EV adoption rates

#### Expected Outcomes

##### Infrastructure Efficiency Assessment

Quantification of current utilization rates
Identification of optimization opportunities
Recommendations for improved efficiency

##### Capacity Forecasting Model

Projected daily and annual energy delivery requirements through 2030
Estimated number of additional charging stations needed
Geographic distribution recommendations

##### Policy Recommendations

Evidence-based strategies to support the County's climate goals
Prioritization framework for infrastructure investments
Monitoring approach for ongoing performance assessment

#### Alignment with Climate Action Plan Goals
This analysis directly supports the County's 2030 Climate Action Plan Zero Emission Mobility Goals by:

Providing data-driven projections to support the 25% passenger EV ownership goal
Identifying infrastructure needs for the 15% commercial EV use goal
Informing strategic placement of the 375 publicly available EV chargers
Establishing a framework for ongoing monitoring and optimization

### Results

The initial baseline forecast model fails to represent the upward trajectory of the test data. This might be improved using the SARIMAX model instead of ARIMA. Furthermore, the data might need a higher differencing value so that it is stationary. Other hyper-parameters can also be adjusted as well.

![image](https://github.com/user-attachments/assets/8ae1b73d-754f-457f-85b1-587ab74e563c)

### Next steps

- Investigate different values for differencing.
- Add seasonality and trends to the model.
- In my searches, a recommendation for the GARCH model was mentioned to better handle the volatility of the data.
- Investigate how outliers and data volatility might be affecting the predictions. In Fig2_C in the [data-analysis-days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-days.ipynb) notebook there are significant outliers that need to be accounted for to improve the preditions.
  ![image](https://github.com/user-attachments/assets/cdabc2ed-4154-4071-83a2-50c2a24e2994)
- Forecast other features such as "Started Sessions" in the "Days" dataset since it might be more stationary.
  
### Outline of project

- [data-analysis-sessions](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-sessions.ipynb)
- [data-analysis-days](https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data-analysis-days.ipynb)

#### Contact and Further Information

https://carlosmunozkampff.com/contact 
https://www.linkedin.com/in/carlos-munoz-kampff/
