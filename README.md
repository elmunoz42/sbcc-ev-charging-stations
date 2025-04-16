### How Can the County of Santa Barbara's Electric Vehicle Charging Infrastructure Data Advance the Implementation of the Zero Emission Vehicle Plan? 

#### Executive Summary

#### Research Question

How can historical electric vehicle (EV) charging station utilization data be used to forecast future charging capacity needs and optimize charging station placement in the County of Santa Barbara to help meet the "Zero Emission Vehicle Plan" goals?

#### Rationale

The County of Santa Barbara (CSB) has ambitious greenhouse gas emission goals. The following excerpt is from a document my CSB liason at the transportation department Jerel Francisco is working on. The document is already in a public draft format and available on the (CSB's transportation department website)[https://www.countyofsb.org/3218/Transportation].

##### County of Santa Barbara Zero Emission Vehicle Plan (Public Draft) May 2025

###### URL: https://cosantabarbara.app.box.com/s/uyds828nxptcrtsjbqssyiu4rpps5odr
###### Excerpt:
"The County has been a leader in climate action, taking steps to reduce greenhouse gas (GHG) emissions and prepare for climate impacts. The 2030 Climate Action Plan (CAP) has a target to reduce community-wide emissions 50% by 2030 (below 2018 levels). On-road vehicle transportation account for 48% of the County's GHG emissions¹. As of 2022, zero emission vehicles (ZEV) make up less than 2% of all vehicles on the road in Santa Barbara County.

To meet State and local emission reduction targets, the CAP includes the following goals to reduce transportation-related emissions:

###### Table 1. 2030 Climate Action Plan Zero Emission Mobility Goals

| CAP Goal | 2030 Goal | 2045 Goal |
|----------|-----------|-----------|
| Increase passenger electric vehicle ownership | 25% | 90% |
| Increase commercial electric vehicle use | 15% | 75% |
| Install at least 375 publicly available electric vehicle chargers | 375 | NA |
| Decarbonize off-road equipment | 21% | 38% |
| Increase bike-mode share | 1% | 5% |

ZEV planning and implementation transects nearly all County operations and community functions, from fleet vehicles, building regulations, infrastructure, parking and energy management. It will require action from both internal County Departments and local community and municipal partners to help implement the Actions (page 31) identified in this plan."

#### Data Sources

CSB's charging stations are integrated with a PowerFlex reporting system with up to date utilization metrics. The historical charging station utilization data including session times, idle times, and energy consumption. Jerel Francisco exported the data from January 1sth 2020 to December 31st 2024 for two types of data exports:
- Sessions: SB-County-County-Public-Portfolio-stations-report-01_01_20-12_31_24.csv:
      - This data has 88919 rows and 30 columns. Each row represents a unique charging session, with information about the charging site, session duration, energy usage etc.
      - The samples include public and CSB fleet vehicle utilization. Since Jerel Francisco had particular interest in the public utilization of the resources we filter out for public usage only early on in our analysis of this dataset.
- Days: "SB-County-County Public reporting 2020-01-01_2024-12-31.csv":
      - This data has 1827 rows and 22 columns. Each row represents a day in the 4 year period with data agregated from all charging sites with information about metric averages.

For a breakdown of all the features please review the respective feature catalogues:
- (Sessions)[]
- (Days)[]

#### Methodology

Time series analysis and forecasting using SARIMAX models to project future capacity needs
Statistical analysis to identify patterns in charging behavior (duration, peak times, idle times)
Classification models to predict potential outages and faulted states
Geographic Information System (GIS) analysis to identify optimal locations for new charging stations
MLOps principles for model development, deployment, and maintenance


A forecasting model that predicts future EV charging capacity requirements for Santa Barbara County
Identification of usage patterns and inefficiencies in current charging infrastructure
Recommendations for optimizing existing station usage by addressing idle time issues
Maps identifying priority areas for new charging station placement based on predicted demand
A framework for continuous monitoring and updating of predictions as new data becomes available




### Project Title

**Author**

#### Executive summary

#### Rationale
Why should anyone care about this question?

#### Research Question
What are you trying to answer?

#### Data Sources
What data will you use to answer you question?

#### Methodology
What methods are you using to answer the question?

#### Results
What did your research find?

#### Next steps
What suggestions do you have for next steps?

#### Outline of project

- [Link to notebook 1]()
- [Link to notebook 2]()
- [Link to notebook 3]()


##### Contact and Further Information