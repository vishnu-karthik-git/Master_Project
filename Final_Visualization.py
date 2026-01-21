import pandas as pd 
import matplotlib.pyplot as plt

solar_charging = pd.read_csv('outputs/EV_load_profile_solar_charging.csv')
grid_charging = pd.read_csv('outputs/EV_load_profile_grid_charging.csv')
pv_grid_charging = pd.read_csv('outputs/EV_load_profile_solar_grid_charging.csv')

# Make a column for total energy consumption in a week
solar_charging['Total_Energy_Consumption_Week'] = solar_charging['EV Mon to Wed consumption [kWh]'] + solar_charging['EV Sat consumption [kWh]']
grid_charging['Total_Energy_Consumption_Week'] = grid_charging['EV charge from Grid [kWh]']

# Add Month column based on Week_Number
solar_charging['Month'] = ((solar_charging['Week_Number'] - 1) * 12 // 52) + 1
grid_charging['Month'] = ((grid_charging['Week_Number'] - 1) * 12 // 52) + 1
pv_grid_charging['Month'] = ((pv_grid_charging['Week_Number'] - 1) * 12 // 52) + 1

# Group by Month and sum
solar_monthly = solar_charging.groupby('Month').sum().reset_index()
grid_monthly = grid_charging.groupby('Month').sum().reset_index()
pv_grid_monthly = pv_grid_charging.groupby('Month').sum().reset_index()

def print_fig(df1: pd.DataFrame,df2: pd.DataFrame, df3: pd.DataFrame ,col: str, yname: str, title: str,timeframe: str = 'Week'):
    # Make a Bar Chart Between two DataFrames

    plt.figure(figsize=(10, 6))
    width = 0.2  # width of the bars
    if timeframe == 'Month':
        x = df1['Month'].unique()
    else:
        x = df1['Week_Number'].unique()
    if title == 'Energy Consumption Comparison' and timeframe == 'Week':
        plt.bar(x + width/2, df2[col], width, label='EV', color='steelblue')
    else:
        plt.bar(x - width, df1[col], width, label='Solar', color='#ff7f0e')
        plt.bar(x , df3[col], width, label='Solar + Grid', color='#1f77b4') 
        plt.bar(x + width, df2[col], width, label='Grid', color='#7f7f7f')
    plt.xlabel('Time in '+timeframe)
    plt.ylabel(yname)
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.savefig('outputs/'+title+' '+timeframe+'.png')

print_fig(solar_monthly,grid_monthly,pv_grid_monthly,'Grid Consumption for Charging [Euros]','Cost [Euros]','Cost Comparison','Month')
print_fig(solar_monthly,grid_monthly,pv_grid_monthly,'Co2 Emssions for the week [kg]','CO2 Emissions [kg]','CO2 Emission Comparison','Month')
print_fig(solar_charging,grid_charging,pv_grid_monthly,'Total_Energy_Consumption_Week','Energy Consumption [kWh]','Energy Consumption Comparison')