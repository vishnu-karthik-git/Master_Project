import pandas as pd
import numpy as np
from Charging_Functions import charge_ev, discharge_ev, charge_ev_grid, get_load_profile_for_grid_charging, get_load_profile_for_period, print_fig
from Emission_Functions import get_emission_for_the_period
from Cost_Functions import calculate_grid_tariff, caculate_feedin_tariff

load_profile = pd.read_csv('inputs/neighbourhood.csv', sep=';')
grid_consumption_solar_charging = pd.DataFrame()
grid_consumption_grid_charging = pd.DataFrame()
del load_profile['unixtimestamp'] 
del load_profile['unixtimestamp.1']

#create a datetime column which has every minute of year 2024
load_profile['Timestamp'] = pd.date_range(start='2024-01-01', end='2024-12-31 23:59', freq='min')
print_fig(load_profile, 'House Load')

#Create a df for EV load profile
ev_load_profile = pd.DataFrame()
ev_load_profile['Week_Number'] = list(range(1, 53))
ev_load_profile_grid = ev_load_profile.copy()

# EV parameters
EV_battery = 58  # kWh
EV_range = 320  # km
EV_power_consumption = EV_battery / EV_range  # kWh per km
EV_daily_distance = 50  # km
EV_daily_consumption = EV_daily_distance * EV_power_consumption  # kWh per day
EV_mon_tue_wed_consumption = EV_daily_consumption * 3  # kWh for Monday, Tuesday, and Wednesday
EV_sat_consumption = EV_daily_consumption  # kWh for Saturday
max_SOC = 0.95  # kWh
SOC_start = max_SOC
week_count = 1

# Constants for indexing specific days of the week 
i_mon_start = 0 # index to start mon of the week
i_thu_start = 3*24*60 # index to start thu of the week 
i_fri_end = 5*24*60
i_sun_start = 6*24*60
i_sun_end = 7*24*60
i_sun_grid = i_sun_start + 20*60 # for choosing 8 pm of sunday as the Grid Charging Time 

def weekly_charge_discharge_pattern_solar_charging(df: pd.DataFrame):
    global grid_consumption_solar_charging
    global SOC_start
    #Assume max SOC at start of Monday
    SOC_after_Mon_Tue_Wed = discharge_ev(SOC_start, EV_mon_tue_wed_consumption, EV_battery)
    print(f'SOC after Mon, Tue, Wed: {round(SOC_after_Mon_Tue_Wed, 3)*100} %')
    #ev_load_profile.loc[week_count - 1, 'SOC_after_Mon_To_Wed'] = round(SOC_after_Mon_Tue_Wed, 3)*100
    ev_load_profile.loc[week_count - 1, 'EV Mon to Wed consumption [kWh]'] = round(SOC_after_Mon_Tue_Wed*EV_battery, 3)

    # EV charging takes place on Thursday and Friday with the exported energy but not exceeding 90% SOC
    SOC_after_Thu_Fri, EV_charging_energy = charge_ev(df, i_thu_start, i_fri_end, SOC_after_Mon_Tue_Wed)
    print(f'EV Charging Energy on Thu and Fri: {round(EV_charging_energy, 3)} kWh')
    # Update final SOC after charging
    print(f'SOC after Charging: {round(SOC_after_Thu_Fri*100, 3)} %')
    #ev_load_profile.loc[week_count - 1, 'SOC_after_Thu_and_Fri'] = round(SOC_after_Thu_Fri, 3)*100
    ev_load_profile.loc[week_count - 1, 'EV Thu to Fri charge [kWh]'] = round((SOC_after_Thu_Fri - SOC_after_Mon_Tue_Wed)*EV_battery, 3)

    # EV discharging on Saturday
    SOC_after_sat = discharge_ev(SOC_after_Thu_Fri, EV_sat_consumption, EV_battery)
    #print(f'EV Consumption for Saturday: {round(EV_sat_consumption, 3)} kWh')
    print(f'SOC after Saturday: {round(SOC_after_sat, 3)*100} %')
    #ev_load_profile.loc[week_count - 1, 'SOC_after_Saturday'] = round(SOC_after_sat, 3)*100
    ev_load_profile.loc[week_count - 1, 'EV Sat consumption [kWh]'] = abs(round((SOC_after_sat - SOC_after_Thu_Fri)*EV_battery, 3))

    # Charge on Sunday from Solar
    SOC_after_Sun, EV_charging_energy = charge_ev(df, i_sun_start, i_sun_end, SOC_after_sat)
    EV_charging_energy_sun_pv = EV_charging_energy
    EV_charging_energy_sun_grid = 0.0
    emission_for_the_week = 0.0
     # If not fully charged, charge from grid as well
    if SOC_after_Sun < (0.95*max_SOC):
        SOC_after_Sun, EV_charging_energy_sun_grid = charge_ev_grid(SOC_after_Sun)
        grid_consumption_week = get_load_profile_for_grid_charging(EV_charging_energy_sun_grid, str(df['Timestamp'].iloc[i_sun_grid]))
        emission_for_the_week = get_emission_for_the_period(grid_consumption_week)
        print(f'Grid Consumption Emissions for the week: {round(emission_for_the_week, 3)} kgCO2')
        grid_consumption_solar_charging = pd.concat([grid_consumption_solar_charging, grid_consumption_week], ignore_index=True)
    EV_charging_energy_sun = EV_charging_energy_sun_pv + EV_charging_energy_sun_grid 
    print(f'EV Charging Energy on Sunday (Solar Charging Strategy): {round(EV_charging_energy_sun, 3)} kWh')
    print(f' - from PV: {round(EV_charging_energy_sun_pv, 3)} kWh')
    print(f' - from Grid: {round(EV_charging_energy_sun_grid, 3)} kWh')
    ev_load_profile.loc[week_count - 1, 'EV sun total charge [kWh]'] = round((SOC_after_Sun-SOC_after_sat)*EV_battery, 3)
    ev_load_profile.loc[week_count - 1, 'EV sun charge from PV [kWh]'] = round(EV_charging_energy_sun_pv, 3)
    ev_load_profile.loc[week_count - 1, 'EV sun charge from Grid [kWh]'] = round(EV_charging_energy_sun_grid, 3)
    ev_load_profile.loc[week_count - 1, 'Grid Consumption for Charging [Euros]'] = calculate_grid_tariff(round(EV_charging_energy_sun_grid, 3))
    ev_load_profile.loc[week_count - 1 ,'Co2 Emssions for the week [KG]'] = round(emission_for_the_week, 3)

    #Update SOC 
    SOC_start = SOC_after_Sun

def weekly_charge_discharge_pattern_grid_charging(df : pd.DataFrame):
    global grid_consumption_grid_charging 

    # EV charging on Sunday Night upto max SOC
    EV_charging_energy_grid = ev_load_profile.loc[week_count - 1, 'EV Mon to Wed consumption [kWh]'] + ev_load_profile.loc[week_count - 1,'EV Sat consumption [kWh]'] 
    grid_consumption_week = get_load_profile_for_grid_charging(EV_charging_energy_grid, str(df['Timestamp'].iloc[i_sun_grid]))
    emission_for_the_week = get_emission_for_the_period(grid_consumption_week)
    print('EV Charging from Grid to reach max SOC on Sunday Night (Grid Charging Strategy)')
    print(f'EV Charging Energy on Sunday Night from Grid: {round(EV_charging_energy_grid, 3)} kWh')
    print(f'Grid Consumption Emissions for the week: {round(emission_for_the_week, 3)} kgCO2')
    grid_consumption_grid_charging = pd.concat([grid_consumption_grid_charging, grid_consumption_week], ignore_index=True)
    ev_load_profile_grid.loc[week_count - 1, 'EV charge from Grid [kWh]'] = round(EV_charging_energy_grid, 3)
    ev_load_profile_grid.loc[week_count - 1, 'Grid Consumption for Charging [Euros]'] = calculate_grid_tariff(round(EV_charging_energy_grid, 3))
    ev_load_profile_grid.loc[week_count - 1 ,'Co2 Emssions for the week [KG]'] = round(emission_for_the_week, 3)

def weekly_feedin_tariff(df : pd.DataFrame):

    Energy_Mon_to_Wed = df.iloc[i_mon_start:i_thu_start]
    Energy_Mon_to_Wed = Energy_Mon_to_Wed[Energy_Mon_to_Wed['total'] < 0]
    Energy_Thu_to_Fri = df.iloc[i_thu_start:i_fri_end]
    Energy_Thu_to_Fri = Energy_Thu_to_Fri[
    Energy_Thu_to_Fri['total'].between(-1.4, 0, inclusive='neither')]
    Energy_Sat = df.iloc[i_fri_end:i_sun_start]
    Energy_Sat = Energy_Sat[Energy_Sat['total'] < 0]
    Energy_Sun = df.iloc[i_sun_start:i_sun_end]
    Energy_Sun = Energy_Sun[
    Energy_Sun['total'].between(-1.4, 0, inclusive='neither')]

    Energy_feedin = abs(Energy_Mon_to_Wed['total'].sum() / 60) + abs(Energy_Thu_to_Fri['total'].sum() / 60) + abs(Energy_Sat['total'].sum() / 60) + abs(Energy_Sun['total'].sum() / 60)
    week_feedin = caculate_feedin_tariff(Energy_feedin)
    ev_load_profile.loc[week_count - 1 ,'Weekly feedin Tariff [Euros]'] = round(week_feedin, 3)
    print(f'Feedin Tariff obtained for this week {caculate_feedin_tariff(Energy_feedin)} Euros')

# Lets create a EV load profile
start_date = np.datetime64('2024-01-01')
end_date = np.datetime64('2024-01-08')

# Get load profile for Every week
for week in range(1, 53):
    print(f'\n--- Week {week} ---')
    print(f'Start Date: {start_date}, End Date: {end_date}')
    load_profile_week = get_load_profile_for_period(load_profile, str(start_date), str(end_date))
    weekly_charge_discharge_pattern_solar_charging(df=load_profile_week)
    weekly_charge_discharge_pattern_grid_charging(df=load_profile_week)
    #weekly_feedin_tariff(df=load_profile_week)
    #Update start_date and end_date for next week
    start_date = start_date + np.timedelta64(7, 'D')
    end_date = end_date + np.timedelta64(7, 'D')
    week_count += 1

# Save the EV load profiles to CSV files
ev_load_profile.to_csv('outputs/EV_load_profile_solar_charging.csv', index=False)
ev_load_profile_grid.to_csv('outputs/EV_load_profile_grid_charging.csv', index=False)

print(f"Annual emission of CO2 in Kg for Solar Charging: {round(ev_load_profile['Co2 Emssions for the week [KG]'].sum(),3)} KG")
print(f"Annual emission of CO2 in Kg for Grid Charging: {round(ev_load_profile_grid['Co2 Emssions for the week [KG]'].sum(),3)} KG")
print(f"Annual cost for energy charged from grid in Solar Charging: {ev_load_profile['Grid Consumption for Charging [Euros]'].sum()} Euros")
print(f"Annual cost for energy charged from grid in Grid Charging: {calculate_grid_tariff(ev_load_profile_grid['EV charge from Grid [kWh]'].sum())} Euros")
#print(f'Annual Feedin Profit {round(ev_load_profile['Weekly feedin Tariff [Euros]'].sum(),2)} Euros')