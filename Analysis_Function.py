import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

load_profile = pd.read_csv('neighbourhood.csv', sep=';')
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
index_1=3*24*60
index_2=5*24*60
index_3=6*24*60
index_4=7*24*60

def print_fig(df: pd.DataFrame):
    # Plot the load profile
    plt.figure(figsize=(10, 6))
    plt.plot(df['Timestamp'], df['total'], label='Load Profile') 
    plt.xlabel('Timestamp')
    plt.ylabel('Load Profile')
    plt.title('Load Profile Over Time')
    plt.ylim(0, -10)  # Adjust y-axis limits as needed
    plt.legend()
    plt.grid()
    plt.show()

# Function to calculate EV charging
def charge_ev(df: pd.DataFrame, index_1: int, index_2: int, current_SOC):
    df = df.iloc[index_1:index_2]
    # print_fig(df)
    extra_power_generated = df[df['total'] < 1.4] # Assuming 1.4 kW is the threshold for ev charging
    total_extra_energy = abs(extra_power_generated['total'].sum() / 60)  # kWh for one minute intervals
    energy_needed_to_full_charge = (max_SOC * EV_battery) - (current_SOC * EV_battery)
    energy_to_charge = min(total_extra_energy, energy_needed_to_full_charge)
    new_SOC = (current_SOC * EV_battery + energy_to_charge) / EV_battery
    return new_SOC, energy_to_charge

def discharge_ev(current_SOC, discharge_energy, battery_capacity):
    available_energy = current_SOC * battery_capacity
    energy_to_discharge = min(discharge_energy, available_energy)
    new_SOC = (current_SOC * battery_capacity - energy_to_discharge) / battery_capacity
    return new_SOC

def charge_ev_grid_and_solar(df: pd.DataFrame, current_SOC):
    df = df.iloc[index_3:index_4]
    # print_fig(df)
    charging_power = df[df['total'] < 0] # Assuming 1.4 kW is the threshold for ev charging
    charging_energy = abs(charging_power['total'].sum() / 60)  # kWh for one minute intervals
    energy_to_charge = (max_SOC * EV_battery) - (current_SOC * EV_battery) 
    energy_to_charge_pv = charging_energy
    energy_to_charge_grid = energy_to_charge - energy_to_charge_pv 
    new_SOC = (current_SOC * EV_battery + energy_to_charge) / EV_battery
    return new_SOC, energy_to_charge_pv, energy_to_charge_grid

def get_load_profile_for_period(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    mask = (df['Timestamp'] >= start_date) & (df['Timestamp'] < end_date)
    return df.loc[mask]

def get_energy_exported(df: pd.DataFrame, index_1: int, index_2: int) -> float:
    df = df.iloc[index_1:index_2]
    power_exported = df[df['total'] < 0]
    total_exported_energy = power_exported['total'].sum() / 60  # kWh for one minute intervals
    return abs(total_exported_energy)

def weekly_charge_discharge_pattern(df: pd.DataFrame):
    #Assume 90% SOC at start of Monday
    SOC_after_Mon_Tue_Wed = discharge_ev(max_SOC, EV_mon_tue_wed_consumption, EV_battery)
    print(f'SOC after Mon, Tue, Wed: {round(SOC_after_Mon_Tue_Wed, 3)*100} %')
    ev_load_profile.loc[week_count - 1, 'SOC_after_Mon_Tue_Wed'] = round(SOC_after_Mon_Tue_Wed, 3)*100

    # EV charging takes place on Thursday and Friday with the exported energy but not exceeding 90% SOC
    SOC_after_Thu_Fri, EV_charging_energy = charge_ev(df, index_1, index_2, SOC_after_Mon_Tue_Wed)
    print(f'EV Charging Energy on Thu and Fri: {round(EV_charging_energy, 3)} kWh')
    # Update final SOC after charging
    print(f'SOC after Charging: {round(SOC_after_Thu_Fri, 3)*100} %')
    ev_load_profile.loc[week_count - 1, 'SOC_after_Thu_and_Fri'] = round(SOC_after_Thu_Fri, 3)*100

    # EV discharging on Saturday
    SOC_after_sat = discharge_ev(SOC_after_Thu_Fri, EV_sat_consumption, EV_battery)
    print(f'EV Consumption for Saturday: {round(EV_sat_consumption, 3)} kWh')
    print(f'SOC after Saturday: {round(SOC_after_sat, 3)*100} %')
    ev_load_profile.loc[week_count - 1, 'SOC_after_sat'] = round(SOC_after_sat, 3)*100

    # Charge on Sunday to 90% SOC
    SOC_after_sun, EV_charging_energy_sun_pv, EV_charging_energy_sun_grid = charge_ev_grid_and_solar(df,SOC_after_sat)
    EV_charging_energy_sun = EV_charging_energy_sun_pv + EV_charging_energy_sun_grid 
    print(f'EV Charging Energy on Sunday: {round(EV_charging_energy_sun, 3)} kWh')
    print(f' - from PV: {round(EV_charging_energy_sun_pv, 3)} kWh')
    print(f' - from Grid: {round(EV_charging_energy_sun_grid, 3)} kWh')
    print(f'SOC after Sunday: {round(SOC_after_sun, 3)*100} %')
    ev_load_profile.loc[week_count - 1, 'SOC_after_sun'] = round(SOC_after_sun, 3)*100

# Lets create a EV load profile
start_date = np.datetime64('2024-01-01')
end_date = np.datetime64('2024-01-08')

# Get load profile for Every week
for week in range(1, 53):
    print(f'\n--- Week {week} ---')
    print(f'Start Date: {start_date}, End Date: {end_date}')
    load_profile_week = get_load_profile_for_period(load_profile, str(start_date), str(end_date))
    #total_exported_energy_on_thu_fri = get_energy_exported(load_profile_week, index_1=3*24*60, index_2=5*24*60)
    #total_energy_exported_on_sun = get_energy_exported(load_profile_week, index_1=6*24*60, index_2=7*24*60)
    weekly_charge_discharge_pattern(df=load_profile_week)
    #Update start_date and end_date for next week
    start_date = start_date + np.timedelta64(7, 'D')
    end_date = end_date + np.timedelta64(7, 'D')
    week_count += 1

print('\nEV Load Profile for the Year 2024:')
print(ev_load_profile)
#print_fig(load_profile_week)



