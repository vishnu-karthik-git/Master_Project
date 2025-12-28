import pandas as pd
import numpy as np
from Charging_Functions import print_fig, get_load_profile_for_period

load_profile = pd.read_csv('inputs/neighbourhood.csv', sep=';')
del load_profile['unixtimestamp'] 
del load_profile['unixtimestamp.1']

#create a datetime column which has every minute of year 2024
load_profile['Timestamp'] = pd.date_range(start='2024-01-01', end='2024-12-31 23:59', freq='T')

start_date = np.datetime64('2024-01-01') + np.timedelta64(24*7, 'D')
end_date = np.datetime64('2024-01-08') + np.timedelta64(24*7, 'D')
new_df = pd.DataFrame()

def prepare_data_for_test(df : pd.DataFrame):
    new_df['Time'] = list(range(len(df)))
    for i in range(len(df)):
        new_df.loc[i,'Power'] = df['total'].iloc[i]
    df_duplicated = new_df.loc[new_df.index.repeat(60)].reset_index(drop=True)
    del df_duplicated['Time']
    df_duplicated['Time'] = list(range(len(df)*60))
    for i in range(len(df_duplicated)):
        df_duplicated.loc[i,'I'] = round(((df_duplicated['Power'].iloc[i])*1000/(3*230)),2)
    print(df_duplicated.head())
    df_duplicated.to_csv('outputs/Preprocessed_data_csv.csv', index=False)

load_profile_week = get_load_profile_for_period(load_profile, str(start_date), str(end_date))
index_3=3*24*60
index_4=4*24*60
df = load_profile_week.iloc[index_3:index_4]
print_fig(df)
df = df.iloc[8*60:12*60]

prepare_data_for_test(df)