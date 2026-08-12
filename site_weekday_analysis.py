import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd

pd.set_option('display.width', 140)
pd.set_option('display.max_columns', 20)

df = pd.read_csv('data/SB-County-County-Public-Portfolio-stations-report-01_01_20-12_31_24.csv',
                  usecols=['Session start', 'kWh delivered', 'Site'])
df['Session start'] = pd.to_datetime(df['Session start'], format='%m-%d-%Y %H:%M:%S', errors='coerce')
df = df.dropna(subset=['Session start'])
df['date'] = df['Session start'].dt.date
df['dow'] = df['Session start'].dt.day_name()

# Restrict to same window as the forecasting analysis for fairness
df = df[df['Session start'] >= '2022-01-01']

print("Sites and total session count:")
print(df['Site'].value_counts())
print()

# Daily energy per site
daily_site = df.groupby(['Site', 'date'])['kWh delivered'].sum().reset_index()
daily_site['dow'] = pd.to_datetime(daily_site['date']).dt.day_name()

dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

print("="*90)
print("Average daily kWh by day-of-week, PER SITE (normalized to that site's own weekly mean = 100)")
print("="*90)
pivot = daily_site.groupby(['Site','dow'])['kWh delivered'].mean().unstack()
pivot = pivot[dow_order]
normalized = pivot.div(pivot.mean(axis=1), axis=0) * 100
print(normalized.round(1))
print()

# Weekday vs weekend gap per site (normalized %)
weekday_cols = dow_order[:5]
weekend_cols = dow_order[5:]
gap = (normalized[weekday_cols].mean(axis=1) - normalized[weekend_cols].mean(axis=1))
print("Weekday-avg minus Weekend-avg (percentage points, +ve = busier on weekdays):")
print(gap.round(1).sort_values())
print()

print("="*90)
print("Same thing but for the COUNTY-WIDE AGGREGATE (all sites summed together)")
print("="*90)
county_daily = daily_site.groupby('date')['kWh delivered'].sum().reset_index()
county_daily['dow'] = pd.to_datetime(county_daily['date']).dt.day_name()
county_profile = county_daily.groupby('dow')['kWh delivered'].mean()[dow_order]
county_norm = county_profile / county_profile.mean() * 100
print(county_norm.round(1))
county_gap = county_norm[weekday_cols].mean() - county_norm[weekend_cols].mean()
print(f"\nCounty aggregate weekday-weekend gap: {county_gap:.1f} percentage points")
