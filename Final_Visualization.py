import pandas as pd 
import matplotlib.pyplot as plt

solar_charging = pd.read_csv('outputs/EV_load_profile_solar_charging.csv')
grid_charging = pd.read_csv('outputs/EV_load_profile_grid_charging.csv')

def print_fig(df1: pd.DataFrame,df2: pd.DataFrame, col: str, yname: str, title: str):
    plt.figure(figsize=(10, 6))
    plt.plot(df1['Week_Number'], df1[col], label='Solar', color='Green') 
    plt.plot(df1['Week_Number'], df2[col], label='Grid', color='red')
    plt.xlabel('Weeks')
    plt.ylabel(yname)
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.savefig('outputs/'+title+'.png')

print_fig(solar_charging,grid_charging,'Grid Consumption for Charging [Euros]','Cost [Euros]','Cost Comparison')
print_fig(solar_charging,grid_charging,'Co2 Emssions for the week [KG]','CO2 Emissions [kG]','CO2 Emission Comparison')