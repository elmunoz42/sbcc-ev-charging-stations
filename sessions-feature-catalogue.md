# Sessions EV Charging Station Data - Feature Catalog
Data file: (Sessions)[https://github.com/elmunoz42/sbcc-ev-charging-stations/blob/main/data/SB-County-County-Public-Portfolio-stations-report-01_01_20-12_31_24.csv]

## Feature description:

| Feature Name | Data Type | Description |
|--------------|-----------|-------------|
| 10-digit session UID | integer | Unique numeric identifier for each charging session |
| Session ID | string | Alternative identifier for the charging session, possibly with prefix/format |
| Session start | string | Timestamp when the charging session began |
| Session end | string | Timestamp when the charging session ended |
| Session duration (minutes) | float | Total time the vehicle was connected to the charger |
| Charging duration (minutes) | float | Time during which the vehicle was actively drawing power |
| Session idle (minutes) | float | Time vehicle remained connected after charging was complete |
| Estimated Completion Time | string | Predicted timestamp when charging would finish |
| kWh delivered | float | Amount of electrical energy provided to the vehicle |
| MAX kW | float | Peak power rate reached during the charging session |
| AVG kW | float | Average power rate throughout the charging session |
| SoC Start | string | State of Charge of the vehicle battery when charging began |
| SoC End | string | State of Charge of the vehicle battery when charging ended |
| User | float | Identifier for the person who initiated the charging session |
| Vehicle | float | Identifier for the specific vehicle being charged |
| EVSE Status | string | Operational status of the Electric Vehicle Supply Equipment |
| EVSEID (PFID) | string | PowerFlex identifier for the specific charging station |
| FSE ID | string | Field Service Engineer identifier for the equipment |
| XB Address | string | Communication address for the charging station |
| Serial # | string | Manufacturer's serial number for the charging equipment |
| EVSE type | string | Model or type of charging station (likely Level 2, DC Fast, etc.) |
| Station Name | string | Descriptive name assigned to the charging station |
| Site | string | Location name where the charging station is installed |
| Site Location | string | Geographic location details (likely address or coordinates) |
| Cost to site | float | Electricity or operational costs incurred by the site host |
| Cost to driver | float | Amount charged to the EV driver for the session |
| Auth Source | string | Method used to authenticate the charging session |
| Auth Details | string | Additional authentication information |
| Fleet | string | Fleet identifier if vehicle belongs to a managed group |
| Vehicle barcode | float | Barcode identifier for the vehicle (currently unused) |