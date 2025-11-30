import pandas as pd
import matplotlib.pyplot as plt

load_profile = pd.read_csv('neighbourhood.csv', sep=';')
del load_profile['unixtimestamp'] 
del load_profile['unixtimestamp.1']

#create a datetime column which has every minute of year 2024
load_profile['Timestamp'] = pd.date_range(start='2024-01-01', end='2024-12-31 23:59', freq='T')
print(load_profile.head())

# create a new df for testing
load_profile_df = load_profile[(load_profile['Timestamp'] >= '2024-01-04') & (load_profile['Timestamp'] < '2024-01-06')]

#Calculate Exported Enrgy in kWh for certain periods
power_exported = load_profile_df[load_profile_df['total'] < 0]
total_exported_energy = power_exported['total'].sum() / 60  # kWh for one minute intervals
print(f'Total Exported Energy: {round(abs(total_exported_energy), 3)} kWh')

# Plot the load profile
plt.figure(figsize=(10, 6))
plt.plot(load_profile_df['Timestamp'], load_profile_df['total'], label='Load Profile') 
plt.xlabel('Timestamp')
plt.ylabel('Load Profile')
plt.title('Load Profile Over Time')
plt.ylim(0, -10)  # Adjust y-axis limits as needed
plt.legend()
plt.grid()
plt.show()

# Function to calculate EV charging
def charge_ev(current_SOC, max_SOC, battery_capacity, charging_energy):
    available_capacity = (max_SOC * battery_capacity) - (current_SOC * battery_capacity)
    energy_to_charge = min(charging_energy, available_capacity)
    new_SOC = (current_SOC * battery_capacity + energy_to_charge) / battery_capacity
    return new_SOC, energy_to_charge

def discharge_ev(current_SOC, discharge_energy, battery_capacity):
    available_energy = current_SOC * battery_capacity
    energy_to_discharge = min(discharge_energy, available_energy)
    new_SOC = (current_SOC * battery_capacity - energy_to_discharge) / battery_capacity
    return new_SOC

# Lets create a EV load profile
EV_battery = 58  # kWh
EV_range = 320  # km
EV_power_consumption = EV_battery / EV_range  # kWh per km
EV_daily_distance = 50  # km
EV_daily_consumption = EV_daily_distance * EV_power_consumption  # kWh per day
EV_mon_tue_wed_consumption = EV_daily_consumption * 3  # kWh for Monday, Tuesday, and Wednesday
EV_sat_consumption = EV_daily_consumption  # kWh for Saturday
print(f'EV Consumption for Mon, Tue, Wed: {round(EV_mon_tue_wed_consumption, 3)} kWh')

#Create a df for EV load profile
ev_load_profile = pd.DataFrame({ 'Timestamp': pd.date_range(start='2024-01-01', end='2024-12-31', freq='T')})
print(ev_load_profile.head())

#Assume 90% SOC at start of Monday
initial_SOC = 0.9  # kWh
final_SOC = discharge_ev(initial_SOC, EV_mon_tue_wed_consumption, EV_battery)
print(f'SOC after Mon, Tue, Wed: {round(final_SOC, 3)*100} %')

# EV charging takes place on Thursday and Friday with the exported energy but not exceeding 90% SOC
max_SOC = 0.9  # kWh
SOC, EV_charging_energy = charge_ev(final_SOC, max_SOC, EV_battery, abs(total_exported_energy))
print(f'EV Charging Energy on Thu and Fri: {round(EV_charging_energy, 3)} kWh')
# Update final SOC after charging
print(f'SOC after Charging: {round(SOC, 3)*100} %')

# EV discharging on Saturday
final_SOC_sat = discharge_ev(SOC, EV_sat_consumption, EV_battery)
print(f'EV Consumption for Saturday: {round(EV_sat_consumption, 3)} kWh')
print(f'SOC after Saturday: {round(final_SOC_sat, 3)*100} %')

# Charge on Sunday to 90% SOC
SOC_sun, EV_charging_energy_sun = charge_ev(final_SOC_sat, max_SOC, EV_battery, abs(total_exported_energy))
print(f'EV Charging Energy on Sunday: {round(EV_charging_energy_sun, 3)} kWh')
print(f'SOC after Sunday: {round(SOC_sun, 3)*100} %')






