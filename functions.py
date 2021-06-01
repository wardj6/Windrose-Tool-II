import pandas as pd
import numpy as np
from __params__ import rename_bom_df_cols, cols_for_wind, cols_for_r
import os
import pathlib
from checks import check_custom_inputs, raise_error


def get_stations_and_files(dir: str) -> pd.DataFrame:
    """
    Returns a dataframe containing 'station_list_complete' that is located in the specified directory
    :param dir: path of the AECOM database
    :return: pandas DataFrame
    """
    sites_file = dir + "\\__station_list_complete.csv"
    try:
        return pd.read_csv(sites_file)
    except FileNotFoundError:
        raise_error(f"The 'station_list_complete.csv' file could not be found in {dir}", FileNotFoundError)


def get_data_source(source: str,
                    location: str,
                    station_id: str) -> str:
    """
    Creates and returns the path in string form for the specified station in AECOM database
    :param source: database identifier from GUI inputs - BOM or OEH etc.
    :param location: directory path for database
    :param station_id: name of station
    :return: string form of path to station's csv data file
    """
    # Get the source data file from the network
    if source == 'BOM':
        data_file = location + "\\" + station_id + "_60min.csv"
        if not os.path.isfile(data_file):
            raise_error(f"Cannot find file for station {station_id} - check if valid", FileNotFoundError)
    else:
        station_list_df = get_stations_and_files(location)
        if station_list_df.loc[station_list_df["Station Name"] == station_id].shape[0] == 0:
            list_of_available_stations = station_list_df['Station Name'].tolist()
            raise_error(f"The entered station does not exist in the {source} database - please select from {list_of_available_stations}",
                        ValueError)
        data_file = location + "\\" + station_list_df.loc[station_list_df["Station Name"] == station_id]["File Name"].iloc[0]
    return data_file


def create_new_folder_for_output(output_folder: str,
                                 station: str) -> str:
    """
    Create new folder for saving wind roses if not already existing
    :param output_folder: path to user specified out put folder
    :param station: station name or ID
    :return: path to new folder in string form
    """
    new_folder_path = output_folder + "\\" + station + "_output"
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
    os.chdir(new_folder_path)
    return new_folder_path


def import_data(data_source: str,
                data_file: str) -> pd.DataFrame:
    """
    Imports the data from one of AECOM's databases
    :param data_source: Database identifier
    :param data_file: path to file
    :return: DataFrame containing 'date', 'ws', 'wd' columns
    """
    if data_source == 'BOM':
        df = pd.read_csv(data_file, parse_dates=['Timestamp'], dayfirst=True)
        df.rename(columns=rename_bom_df_cols, inplace=True)
        # convert from km/h to m/s
        df["WS (m/s)"] = df["WS (m/s)"] / 3.6
        wind_df = df[cols_for_wind].copy()
    else:
        df = pd.read_csv(data_file, parse_dates=['Date'], dayfirst=True)
        wind_df = df[cols_for_wind].copy()
    wind_df.rename(columns=cols_for_r, inplace=True)
    return wind_df


def replace_calms(df: pd.DataFrame,
                  calms_thres: float) -> pd.DataFrame:
    """
    Replaces wind direction values with Openair's null flag -999 for wind speed values less than the calms threshold
    :param df: input dataframe
    :param calms_thres: threshold for calms in m/s
    :return: converted dataframe
    """
    out_df = df
    out_df.loc[out_df['ws'] < calms_thres, 'wd'] = -999
    return out_df


def make_image_transparent(image_to_process: str):
    """
    Takes an images and converts white pixels to transparent
    :param image_to_process: path to image
    """
    from PIL import Image
    img = Image.open(image_to_process)
    img = img.convert("RGBA")
    pix_data = img.load()
    width, height = img.size
    for y in range(height):
        for x in range(width):
            if pix_data[x, y] == (255, 255, 255, 255):
                pix_data[x, y] = (255, 255, 255, 0)
    transparent_image = image_to_process.replace(".png", "_transparent.png")
    img.save(transparent_image, "PNG")


def get_custom_data_period(date_string: str) -> list:
    """
    Converts the input date string from the GUI into a list of pandas date time objects
    :param date_string:
    :raise: ValueError if date string format is not correct
    :return: dates as list of pandas date time objects
    """
    dates = date_string.split("-")
    try:
        dates_i = [pd.to_datetime(x.strip(), dayfirst=True) for x in dates]
    except:
        raise_error("The manually entered date period is not in the correct format and cannot be parsed - try again.", ValueError)
    else:
        return dates_i


def get_rose_types_and_layouts(all_hours: bool,
                               seasons: bool,
                               seasons_daylight: bool,
                               monthly: bool,
                               annual_daylight: bool) -> (list, list):
    """
    Parses the rose type GUI check box inputs and generates a list of openair rose types and a list of the figure layouts to pass to openair
    :param all_hours: gui checkbox option
    :param seasons: gui checkbox option
    :param seasons_daylight: gui checkbox option
    :param monthly: gui checkbox option
    :param annual_daylight: gui checkbox option
    :return: rose type list, layout list
    """
    roses = []
    layouts = []
    count = 0
    if all_hours:
        roses.append(['default'])
        layouts.append([1,1])
        count += 1
    if seasons:
        roses.append(['season'])
        layouts.append([2,2])
        count += 1
    if seasons_daylight:
        roses.append(['season', 'daylight'])
        layouts.append([4,2])
        count += 1
    if monthly:
        roses.append(['month'])
        count += 1
        layouts.append([3, 4])
    if annual_daylight:
        roses.append(['daylight'])
        layouts.append([2,1])
        count += 1
    if count == 0:
        roses = [['default'], ['season', 'daylight'], ['month'], ['season'], ['daylight']]
        layouts = [[1, 1], [4, 2], [3, 4], [2, 2], [2, 1]]
    return roses, layouts


def slice_by_custom_dates(wind_df: pd.DataFrame,
                          data_period: str) -> pd.DataFrame:
    """
    Slices the data according to the custom dates
    :param wind_df: input data frame
    :param data_period: custom user data period
    :return: sliced data frame
    """
    wind_start_year = wind_df["date"][0].year
    wind_end_year = wind_df["date"][len(wind_df.index) - 1].year
    if data_period:
        dates = get_custom_data_period(data_period)
        custom_start = dates[0]
        if len(dates) == 1:
            custom_end = custom_start + pd.to_timedelta('23H')
        else:
            custom_end = dates[1] + pd.to_timedelta('23H')
        mask = (wind_df["date"] >= custom_start) & (wind_df["date"] <= custom_end)
        wind_df = wind_df.loc[mask]

        if custom_end.year < wind_start_year:
            raise_error(f'The custom dates are before the first data available ({wind_start_year})', ValueError)
        if custom_start.year >= wind_start_year:
            wind_start_year = custom_start.year
        else:
            print('\nThe custom start date is before the first data available - processing wind rose from'
                  ' start of data availability\n')
        if custom_end.year <= wind_end_year:
            wind_end_year = custom_end.year
        else:
            print('\nThe custom end date is after the last data available - processing wind rose to end '
                  'of data availability\n')
    print(f"\nThe processed wind data period is {wind_start_year} to {wind_end_year}\n")
    return wind_df


def parse_custom_hours(cust_hrs: str) -> list:
    """
    Parses the custom hours entered in the GUI and return a list of hours to use as a filter
    :param cust_hrs: optional custom hours string from GUI
    :return: list of custom hours
    """
    hour_list = []
    hours = cust_hrs.split(",")
    for item in hours:
        if "-" in item:
            sub_hours = item.split("-")
            sub_hours_set = list(np.arange(int(sub_hours[0]), int(sub_hours[1]) + 1))
            hour_list.extend(sub_hours_set)
        else:
            hour_list.append(int(item))
    if len(hour_list) != 24:
        print(f"The custom sub set of hours included are {hour_list}")
    return hour_list


def filter_df_by_hours(df: pd.DataFrame,
                       hours: list) -> pd.DataFrame:
    """
    Slices the data according to the custom hours
    :param df: input data frame
    :param hours: list of hours to slice
    :return: sliced data frame
    """
    filtered_df = df.copy()
    filtered_df.index = filtered_df['date']
    filtered_df['hour'] = filtered_df.index.hour
    filtered_df = filtered_df.loc[filtered_df['hour'].isin(hours)]
    filtered_df = filtered_df.drop(columns=['hour'])
    filtered_df.reset_index(drop=True, inplace=True)
    return filtered_df


def slice_by_custom_hours(wind_df: pd.DataFrame,
                          selected_hours: str) -> pd.DataFrame:
    """
    Read in custom hours or set to default, then filter data by hours
    :param wind_df: input data frame
    :param selected_hours: string of custom hours from GUI
    :return: sliced data frame
    """
    if selected_hours:
        hour_list = parse_custom_hours(selected_hours)
    else:
        hour_list = np.arange(0,24)
    return filter_df_by_hours(wind_df, hour_list)


def generate_annual_wind_dict(df: pd.DataFrame) -> dict:
    """
    Split data into annual data frames and place in dictionary
    :param df: input data frame
    :return: dictionary of annual data frames
    """
    annual_wind_dict = {}
    start_year = df["date"].iloc[0].year
    end_year = df["date"].iloc[-1].year
    import datetime as dt
    for year in range(start_year, end_year + 1):
        start_date = dt.datetime(year=year, month=1, day=1, hour=1)
        end_date = dt.datetime(year=year, month=12, day=31, hour=23)
        annual_df = pd.DataFrame(None)
        annual_df = df.loc[df.date >= start_date]
        annual_df = annual_df.loc[annual_df.date <= end_date]
        annual_wind_dict[year] = annual_df
    return annual_wind_dict


def windrose_data_not_empty(df: pd.DataFrame,
                            raise_e: bool):
    """
    Checks whether a wind dataframe is empty or containing only null or missing flags for WS or WD columns
    :param: df: Pandas dataframe containing 'ws' and wd' columns
    :param: raise_e: True if error is to be raised
    :return: True if dataframe not empty, False if empty
    :raise: ValueError if empty and raise_e is True
    """
    ws_all_missing_flags = df['ws'].mean() == -999
    wd_all_missing_flags = df['wd'].mean() == -999
    empty = len(df) == 0
    ws_null = df['ws'].isna().sum() == df.shape[0]
    wd_null = df["wd"].isna().sum() == df.shape[0]

    if ws_all_missing_flags or wd_all_missing_flags or empty or ws_null or wd_null:
        if raise_e:
            raise_error("The parsed dataframe contains no data - no wind roses generated", ValueError)
        else:
            return False
    else:
        return True


def import_csv_data(file: str,
                    header_lines: int,
                    start_date: str,
                    start_hour: int,
                    num_hours: int,
                    ws_col: str,
                    wd_col: str) -> pd.DataFrame:
    """
    Imports data from user selected CSV file
    IMPORTANT - this function generates a new date time index for the data and assumes that no hours are missing in the data.
    If there are hours missing, then the CSV should be edited to include these hours
    :param file: path to CSV file
    :param header_lines: number of header rows before data begins in CSV file
    :param start_date: start date of CSV data
    :param start_hour: start hour of CSV data
    :param num_hours: Total number of rows of data in CSV - not including header rows
    :param ws_col: alphabetic column identifier for WS data
    :param wd_col: alphabetic column identifier for WD data
    :return: data frame containing wind data
    """
    # Convert the alphabetic cols provided in the GUI to numerical versions
    col_list = np.arange(0, 25)
    csv_col_dict = dict(zip(list('abcdefghijklmnopqrstuvwxyz'), np.arange(0, 25)))
    ws_col = csv_col_dict.get(ws_col.lower())
    wd_col = csv_col_dict.get(wd_col.lower())

    check_custom_inputs("header_lines", header_lines)
    csv_working_df = pd.read_csv(file, header=None, skiprows=header_lines)
    csv_working_df.dropna(how='all', axis=0, inplace=True)

    # make wind df
    csv_wind_df = pd.DataFrame()
    try:
        start_datetime = pd.to_datetime(start_date, dayfirst=True) + pd.Timedelta(hours=start_hour)
        csv_date_range = pd.date_range(start=start_datetime, periods=num_hours, freq='h')
    except:
        raise_error("Check start date is in the correct format '1/1/2019'", ValueError)
    else:
        csv_wind_df['date'] = csv_date_range
    try:
        csv_wind_df['ws'] = csv_working_df.iloc[:, ws_col].tolist()
        csv_wind_df['wd'] = csv_working_df.iloc[:, wd_col].tolist()
    except:
        raise_error("Input number of hours does not match the length of the csv", ValueError)
    # convert missing aermod values (i.e. 999 or 9999) to NaN
    csv_wind_df.ws = csv_wind_df.apply(lambda x: np.nan if x['ws'] > 100 else x['ws'], axis=1)
    csv_wind_df.wd = csv_wind_df.apply(lambda x: np.nan if x['wd'] > 360 else x['wd'], axis=1)

    return csv_wind_df


def update_output_path(output_folder: pathlib.WindowsPath,
                       station_id: str,
                       rose_type: list,
                       year_string: str) -> str:
    """
    Creates an output path to save the wind rose as a PNG image
    :param output_folder: folder path
    :param station_id: station name or ID
    :param rose_type: Openair type of rose -e.g. 'season'
    :param year_string: Year string for annual wind roses - set to '' for all-data wind roses
    :return: Full path to output file in string format
    """
    output_file = str(output_folder) + "\\" + station_id + "_" + "_".join(rose_type) + "_" + year_string + ".png"
    return output_file



