# Days EV Charging Station Data - Feature Catalog

| Feature Name | Data Type | Description |
|--------------|-----------|-------------|
| Day | string | Date of recorded charging station activity |
| Started Sessions | integer | Number of charging sessions initiated during the day |
| Completed Sessions | integer | Number of charging sessions successfully completed during the day |
| Microsessions | integer | Number of very short charging sessions (likely less than a few minutes) |
| AVG session duration (minutes) | float | Average total time vehicles were connected to chargers |
| AVG charging duration (minutes) | float | Average time vehicles were actively drawing power |
| AVG session idle (minutes) | float | Average time vehicles remained connected after charging completed |
| Energy delivered (kWh) | float | Total electrical energy provided to vehicles |
| AVG kWh delivered per session (kWh) | float | Average amount of energy delivered per charging session |
| Max kWh delivered per session (kWh) | float | Maximum amount of energy delivered in a single charging session |
| Max kW hour (kW) | string | Hour of the day with peak power demand |
| GHGs avoided (lbs) | float | Estimated greenhouse gas emissions avoided by using electric vs. gasoline vehicles |
| Gasoline avoided (Gal) | float | Estimated gallons of gasoline not consumed due to EV usage |
| Electric miles provided (mi) | float | Estimated electric vehicle miles enabled by the energy delivered |
| Potential revenue ($) | float | Maximum possible revenue based on pricing policies |
| Collected revenue ($) | float | Actual revenue collected from charging sessions |
| Discounts granted ($) | float | Value of discounts or promotions applied to charging sessions |
| Utilization (%) | float | Percentage of time charging stations were in use |
| Max Utilization (%) | string | Time period with highest utilization percentage |
| Faulted Stations | string | Stations experiencing technical issues or malfunctions |
| Time in Faulted State (hours) | float | Duration stations were non-operational due to faults |
| Uptime (%) | string | Percentage of time stations were operational and available for use |