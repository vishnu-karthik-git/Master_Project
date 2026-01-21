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