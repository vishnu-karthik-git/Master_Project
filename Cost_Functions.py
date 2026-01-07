
tariff = 0.48 # 0.48 euros per kWh
feedIn_tariff = 0.08 # 0.08 euros per kWh

def calculate_grid_tariff(Energy_consumed):
    return round((Energy_consumed*tariff),3)

def caculate_feedin_tariff(Energy_feedin):
    return round((Energy_feedin*feedIn_tariff),3)


