des_data_network_dir = r"path to dir"
bom_data_network_dir = r'path to dir'
oeh_data_network_dir = r"path to dir"
epav_data_network_dir = r"path to dir"

data_source_dict = {
    'BOM': bom_data_network_dir,
    'DES': des_data_network_dir,
    'OEH': oeh_data_network_dir,
    'EPAV': epav_data_network_dir
}

rename_bom_df_cols = {
    'Wind (1 minute) speed in km/h': 'WS (m/s)',
    'Vector Average Wind Direction (in degrees)': 'WD (deg)',
    'Timestamp': 'Date'
}

cols_for_wind = ['WS (m/s)', 'WD (deg)', 'Date']

cols_for_r = {
    'WS (m/s)': 'ws',
    'WD (deg)': 'wd',
    'Date': 'date'
}

r_type_size_dict = {
    'default': [800, 800],
    'season_daylight': [1500, 1000],
    'month': [1200, 1600],
    'season': [1200, 1200],
    'daylight': [1200, 800]
}