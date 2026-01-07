import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# EV parameters
EV_battery = 58  # kWh
max_SOC = 0.95  # SOC percentage

np.random.seed(42)   # set the seed

def print_fig(df: pd.DataFrame, name: str):
    # Plot the load profile
    plt.figure(figsize=(10, 6))
    plt.plot(df['Timestamp'], df['total'], label='Load Profile') 
    plt.xlabel('Timestamp')
    plt.ylabel('Load Profile')
    plt.title('Load Profile Over Time')
    plt.ylim(-7, 7)  # Adjust y-axis limits as needed
    plt.legend()
    plt.grid()
    plt.savefig('outputs/'+name+'.png')

def get_load_profile_for_period(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    mask = (df['Timestamp'] >= start_date) & (df['Timestamp'] < end_date)
    return df.loc[mask]

# Function to calculate EV charging
def charge_ev(df: pd.DataFrame, index_1: int, index_2: int, current_SOC):
    df = df.iloc[index_1:index_2]
    extra_power_generated = df[df['total'] < -1.4] # Assuming 1.4 kW is the threshold for ev charging
    total_extra_energy = abs(extra_power_generated['total'].sum() / 60)  # kWh for one minute intervals
    total_extra_energy = total_extra_energy * 0.98 # only 98 % efficiency
    energy_needed_to_full_charge = (max_SOC * EV_battery) - (current_SOC * EV_battery)
    energy_to_charge = min(total_extra_energy, energy_needed_to_full_charge)
    new_SOC = (current_SOC * EV_battery + energy_to_charge) / EV_battery

    return new_SOC, energy_to_charge

def discharge_ev(current_SOC, discharge_energy, battery_capacity):
    available_energy = current_SOC * battery_capacity
    discharge_energy = discharge_energy * (1 + np.random.uniform(-0.10, 0.10))
    energy_to_discharge = min(discharge_energy, available_energy)
    new_SOC = (current_SOC * battery_capacity - energy_to_discharge) / battery_capacity

    return new_SOC

def get_energy_exported(df: pd.DataFrame, index_1: int, index_2: int) -> float:
    df = df.iloc[index_1:index_2]
    power_exported = df[df['total'] < 0]
    total_exported_energy = power_exported['total'].sum() / 60  # kWh for one minute intervals

    return abs(total_exported_energy)

def charge_ev_grid(current_SOC):
    energy_needed_to_full_charge = (max_SOC * EV_battery) - (current_SOC * EV_battery)
    charge_power_rate = 11 * 0.98  # account for ~2% losses
    time_to_charge = energy_needed_to_full_charge / charge_power_rate if charge_power_rate > 0 else 0
    energy_to_charge_grid = energy_needed_to_full_charge
    new_SOC = max_SOC
    
    return new_SOC, energy_to_charge_grid

def get_load_profile_for_grid_charging(Energy_to_charge: float, start_date: str) -> pd.DataFrame:
    df = pd.DataFrame()
    time_for_charging = Energy_to_charge / (11 * 0.98)  # hours
    end_date = pd.to_datetime(start_date) + pd.Timedelta(hours=time_for_charging)
    df['Timestamp'] = pd.date_range(start=start_date, end=end_date, freq='min')[:-1]
    df['Grid_Charging_Load_kW'] = 11  # kW

    return df