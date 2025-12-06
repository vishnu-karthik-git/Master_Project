import pandas as pd
import numpy as np
from Charging_functions import charge_ev, discharge_ev, charge_ev_grid, print_fig, get_load_profile_for_grid_charging
from Emission_Function import get_emission_for_the_period

load_profile = pd.read_csv('inputs/neighbourhood.csv', sep=';')
grid_consumption = pd.DataFrame()
del load_profile['unixtimestamp'] 
del load_profile['unixtimestamp.1']

#create a datetime column which has every minute of year 2024
load_profile['Timestamp'] = pd.date_range(start='2024-01-01', end='2024-12-31 23:59', freq='T')

#Create a df for EV load profile
ev_load_profile = pd.DataFrame()
ev_load_profile['Week_Number'] = list(range(1, 53))

# EV parameters
EV_battery = 58  # kWh
EV_range = 320  # km
EV_power_consumption = EV_battery / EV_range  # kWh per km
EV_daily_distance = 50  # km
EV_daily_consumption = EV_daily_distance * EV_power_consumption  # kWh per day
EV_mon_tue_wed_consumption = EV_daily_consumption * 3  # kWh for Monday, Tuesday, and Wednesday
EV_sat_consumption = EV_daily_consumption  # kWh for Saturday
max_SOC = 0.9  # kWh
week_count = 1

# Constants for indexing specific days of the week 
index_1=3*24*60 # index to start thu of the week 
index_2=5*24*60
index_3=6*24*60
index_4=7*24*60
index_5=index_3 + 20*60 # for choosing 8 pm of sunday as the Grid Charging Time 

def get_load_profile_for_period(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    mask = (df['Timestamp'] >= start_date) & (df['Timestamp'] < end_date)
    return df.loc[mask]

def weekly_charge_discharge_pattern(df: pd.DataFrame):
    global grid_consumption
    #Assume 90% SOC at start of Monday
    SOC_after_Mon_Tue_Wed = discharge_ev(max_SOC, EV_mon_tue_wed_consumption, EV_battery)
    print(f'SOC after Mon, Tue, Wed: {round(SOC_after_Mon_Tue_Wed, 3)*100} %')
    ev_load_profile.loc[week_count - 1, 'SOC_after_Mon_To_Wed'] = round(SOC_after_Mon_Tue_Wed, 3)*100
    ev_load_profile.loc[week_count - 1, 'EV_mon_to_wed_consumption_kWh'] = round(SOC_after_Mon_Tue_Wed*EV_battery, 3)

    # EV charging takes place on Thursday and Friday with the exported energy but not exceeding 90% SOC
    SOC_after_Thu_Fri, EV_charging_energy = charge_ev(df, index_1, index_2, SOC_after_Mon_Tue_Wed)
    print(f'EV Charging Energy on Thu and Fri: {round(EV_charging_energy, 3)} kWh')
    # Update final SOC after charging
    print(f'SOC after Charging: {round(SOC_after_Thu_Fri*100, 3)} %')
    ev_load_profile.loc[week_count - 1, 'SOC_after_Thu_and_Fri'] = round(SOC_after_Thu_Fri, 3)*100
    ev_load_profile.loc[week_count - 1, 'EV_thu_to_fri_charge_kWh'] = round((SOC_after_Thu_Fri - SOC_after_Mon_Tue_Wed)*EV_battery, 3)

    # EV discharging on Saturday
    SOC_after_sat = discharge_ev(SOC_after_Thu_Fri, EV_sat_consumption, EV_battery)
    #print(f'EV Consumption for Saturday: {round(EV_sat_consumption, 3)} kWh')
    print(f'SOC after Saturday: {round(SOC_after_sat, 3)*100} %')
    ev_load_profile.loc[week_count - 1, 'SOC_after_Saturday'] = round(SOC_after_sat, 3)*100
    ev_load_profile.loc[week_count - 1, 'EV_sat_consumption_kWh'] = abs(round((SOC_after_sat - SOC_after_Thu_Fri)*EV_battery, 3))

    # Charge on Sunday from Solar
    SOC_after_Sun, EV_charging_energy = charge_ev(df, index_3, index_4, SOC_after_sat)
    EV_charging_energy_sun_pv = EV_charging_energy
    EV_charging_energy_sun_grid = 0.0
    emission_for_the_week = 0.0
     # If not fully charged, charge from grid as well
    if SOC_after_Sun < max_SOC:
        SOC_after_Sun, EV_charging_energy_sun_grid = charge_ev_grid(SOC_after_Sun)
        grid_consumption_week = get_load_profile_for_grid_charging(EV_charging_energy_sun_grid, str(df['Timestamp'].iloc[index_5]))
        emission_for_the_week = get_emission_for_the_period(grid_consumption_week)
        print(f'Grid Consumption Emissions for the week: {round(emission_for_the_week, 3)} kgCO2')
        grid_consumption = pd.concat([grid_consumption, grid_consumption_week], ignore_index=True)
    EV_charging_energy_sun = EV_charging_energy_sun_pv + EV_charging_energy_sun_grid 
    print(f'EV Charging Energy on Sunday: {round(EV_charging_energy_sun, 3)} kWh')
    print(f' - from PV: {round(EV_charging_energy_sun_pv, 3)} kWh')
    print(f' - from Grid: {round(EV_charging_energy_sun_grid, 3)} kWh')
    ev_load_profile.loc[week_count - 1, 'EV_sun_total_charge_kWh'] = round((SOC_after_Sun-SOC_after_sat)*EV_battery, 3)
    ev_load_profile.loc[week_count - 1, 'EV_sun_charge_from_PV_kWh'] = round(EV_charging_energy_sun_pv, 3)
    ev_load_profile.loc[week_count - 1, 'EV_sun_charge_from_Grid_kWh'] = round(EV_charging_energy_sun_grid, 3)
    ev_load_profile.loc[week_count - 1 ,'Emssions_kgCO2_for_the_week'] = round(emission_for_the_week, 3)

# Lets create a EV load profile
start_date = np.datetime64('2024-01-01')
end_date = np.datetime64('2024-01-08')

# Get load profile for Every week
for week in range(1, 53):
    print(f'\n--- Week {week} ---')
    print(f'Start Date: {start_date}, End Date: {end_date}')
    load_profile_week = get_load_profile_for_period(load_profile, str(start_date), str(end_date))
    weekly_charge_discharge_pattern(df=load_profile_week)
    #Update start_date and end_date for next week
    start_date = start_date + np.timedelta64(7, 'D')
    end_date = end_date + np.timedelta64(7, 'D')
    week_count += 1

print('\nEV Load Profile for the Year 2024:')
print(ev_load_profile)
