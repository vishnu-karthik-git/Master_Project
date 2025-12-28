import pandas as pd
import matplotlib.pyplot as plt 

test_name = "dynamic_test"
path = "test_data/"+test_name+"/DUT-'Amperfied_5.1.1'.csv"
df = pd.read_csv(path)
cap_rate = 10

Energy_Grid = 0.0
Energy_Solar = 0.0
Energy_Ev = 0.0

def preprocess_data(df: pd.DataFrame)->pd.DataFrame:
    df['Power_Surplus'] = abs(df['CINERGIA HOUSE.Pu'] + df['CINERGIA HOUSE.Pv'] + df['CINERGIA HOUSE.Pw'])
    df['Power_EV'] = df['CINERGIA EV.Pu'] + df['CINERGIA EV.Pv'] + df['CINERGIA EV.Pw'] 
    df['Power_Grid'] = df['Janitza UMG508.Pna'] + df['Janitza UMG508.Pnb'] + df['Janitza UMG508.Pnc']
    return df

def visualize_df(df: pd.DataFrame):
    plt.figure(figsize=(10, 6))
    plt.plot(df['Time'], df['Power_Surplus'], label='Suplus', color='Darkorange') 
    plt.plot(df['Time'], df['Power_EV'], label='Wallbox', color='steelblue')
    plt.xlabel('Time')
    plt.ylabel('Power in Watts')
    plt.title('EV Charging Over Time')
    #plt.ylim(0, -10)  # Adjust y-axis limits as needed
    plt.legend()
    plt.grid()
    plt.show()

def energy_calculation(df: pd.DataFrame):
    global Energy_Solar, Energy_Ev, Energy_Grid
    for i in range(0, len(df), cap_rate):
        Energy_Solar += (df['Power_Surplus'].iloc[int(i)]/3600)
        Energy_Ev += (df['Power_EV'].iloc[int(i)]/3600)
        Energy_Grid += (df['Power_Grid'].iloc[int(i)]/3600)

modified_df = preprocess_data(df)
#visualize_df(modified_df)
energy_calculation(modified_df)
print(f"Energy produced from Solar {round(Energy_Solar/1000,2)} kWh")
print(f"Energy charged to Ev {round(Energy_Ev/1000,2)} kWh")
print(f"Energy consumed from Grid {round(Energy_Grid/1000,2)} kWh")