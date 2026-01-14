import pandas as pd
from Charging_Functions import print_fig
from Cost_Functions import calculate_grid_tariff
from Emission_Functions import get_emission_for_the_period

load_profile = pd.read_csv('inputs/neighbourhood_0.csv', sep=';')
del load_profile['unixtimestamp'] 
del load_profile['unixtimestamp.1']

#create a datetime column which has every minute of year 2024
load_profile['Timestamp'] = pd.date_range(start='2024-01-01', end='2024-12-31 23:59', freq='min')
print_fig(load_profile, 'Grid Only Load')

Total_Energy_Consumption_Year = load_profile['total'].sum() / 60  # kWh for one minute intervals
# print(f'Total Energy Consumption in the Year 2024 (Grid Only): {round(Total_Energy_Consumption_Year, 2)} kWh')
print(f'Cost of Energy Consumption in the Year 2024 (Grid Only): {calculate_grid_tariff(Total_Energy_Consumption_Year)} Euros')  # Assuming a flat rate of 0.20 Euros per kWh
print(f'Emissions of CO2 in the Year 2024 (Grid Only): {round(get_emission_for_the_period(load_profile), 2)} KG')