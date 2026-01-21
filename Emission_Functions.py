import pandas as pd 
import math
import numpy as np 

emission_profile = pd.read_csv('inputs/DE_2024_hourly.csv', sep=',')
emission_profile['Datetime'] = pd.to_datetime(emission_profile['Datetime']) 
emission_profile = emission_profile.set_index('Datetime')

def get_emission_for_the_period(df: pd.DataFrame):
    global emission_profile
    df = df.copy()
    new_df = pd.DataFrame()
    # Since df has minute-level data, we need to resample it to hourly to match the emission profile
    start_time  = df['Timestamp'].iloc[0]
    end_time = df['Timestamp'].iloc[-1]
    # Calculate number of hours between start_time and end_time
    num_hours = math.ceil((end_time - start_time).total_seconds() / 3600)
    time = start_time
    df = df.set_index('Timestamp')
    emissions_in_kg_per_kWh = 0
    for i in range(num_hours):
        new_df.loc[i, 'Time'] = time
        energy = df.loc[time : (time+np.timedelta64(59, 'm'))]
        if 'Grid_Charging_Load_kW' in energy.columns:
            energy_consumed = energy['Grid_Charging_Load_kW'].sum()/60
        else:
            energy_consumed = energy[energy['total'] > 0]['total'].sum()/60
        new_df.loc[i, 'Energy_consumed_kWh'] = energy_consumed
        emission_df = emission_profile.loc[time]
        emission = (emission_df['Carbon intensity g/kWh (direct)'].sum() * energy_consumed) / 1000
        new_df.loc[i, 'Emission'] = emission
        emissions_in_kg_per_kWh += emission
        time += np.timedelta64(1, 'h')

    return emissions_in_kg_per_kWh

def calculate_emission_with_partial_hour(df: pd.DataFrame, start_time):
    """
    Calculate emissions handling partial hours.
    If charging starts at 8:50, calculate energy from 8:50-9:00 
    and multiply by emissions of hour 8:00
    """
    global emission_profile
    df = df.copy()
    df = df.set_index('Timestamp')
    
    emissions_total = 0
    current_time = start_time
    end_time = df.index[-1]
    
    while current_time < end_time:
        # Calculate the hour boundary
        hour_start = current_time.floor('h')  # Start of current hour (e.g., 8:00)
        hour_end = hour_start + pd.Timedelta(hours=1)  # End of current hour (e.g., 9:00)
        
        # Determine the actual period to calculate (might be partial)
        period_start = current_time
        period_end = min(hour_end, end_time)
        
        # Calculate minutes in this period
        duration_minutes = (period_end - period_start).total_seconds() / 60
        
        # Get energy consumed in this period
        period_data = df.loc[period_start:period_end]
        if 'Grid_Charging_Load_kW' in period_data.columns:
            energy_consumed = period_data['Grid_Charging_Load_kW'].sum() / 60  # Convert to kWh
        else:
            energy_consumed = period_data[period_data['total'] > 0]['total'].sum() / 60
        
        # Get emission factor for the HOUR (use hour_start time for lookup)
        emission_df = emission_profile.loc[hour_start]
        emission_rate = emission_df['Carbon intensity g/kWh (direct)']
        
        # Calculate emission for this period
        emission = (emission_rate * energy_consumed) / 1000  # Convert g to kg
        emissions_total += emission
        
        # Move to next hour
        current_time = hour_end
    
    return emissions_total

