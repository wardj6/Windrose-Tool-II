import pytest
import pandas as pd
import datetime
from __params__ import epav_data_network_dir
from functions import get_stations_and_files, get_data_source, import_data, replace_calms, get_custom_data_period
from functions import get_rose_types_and_layouts, slice_by_custom_dates, parse_custom_hours, filter_df_by_hours
from functions import slice_by_custom_hours, generate_annual_wind_dict, windrose_data_not_empty, import_csv_data

test_csv_file = r"C:\Users\wardj6\PycharmProjects\WRT_II\Test_Data\Alphington.csv"


def test_get_stations_and_files():
    dir = epav_data_network_dir
    sites_file = get_stations_and_files(dir)
    assert isinstance(sites_file, pd.DataFrame)
    wrong_dir = r"C:\Users\wardj6\PycharmProjects\WRT_II\Test_Dat"
    with pytest.raises(FileNotFoundError):
        assert get_stations_and_files(wrong_dir)


def test_get_data_source():
    source = "EPAV"
    location = epav_data_network_dir
    station_id = 'alphington'
    alphington_path = r"\\auntl1fp001\Groups\!ENV\Team_AQ\Modelling\+Support_Data\+EPAV Data\Combined\Alphington.csv"
    assert get_data_source(source, location, station_id) == alphington_path


def test_import_data():
    data_source = "EPAV"
    data_file = r"\\auntl1fp001\Groups\!ENV\Team_AQ\Modelling\+Support_Data\+EPAV Data\Combined\Alphington.csv"
    wind_df = import_data(data_source, data_file)
    assert isinstance(wind_df, pd.DataFrame)
    assert list(wind_df.columns) == ['ws', 'wd', 'date']


def test_replace_calms():
    test_df = pd.DataFrame({
        "ws": [0.4, 0.5, 0.6],
        "wd": [180, 180, 180],
        "date": [1, 2, 3]
    },
        index=[0,1,2])
    calms = 0.5
    calms_replaced_df = replace_calms(test_df, calms)
    assert list(calms_replaced_df["ws"]) == [0.4, 0.5, 0.6]
    assert list(calms_replaced_df["wd"]) == [-999, 180, 180]
    assert list(calms_replaced_df["date"]) == [1, 2, 3]


def test_get_custom_data_period():
    test_date_1 = "1/1/2019-31/12/2019"
    test_date_2 = "1/1/2019 31/12/2019"
    date_1 = get_custom_data_period(test_date_1)
    assert isinstance(date_1[0], datetime.datetime)
    assert isinstance(date_1[1], datetime.datetime)
    with pytest.raises(ValueError):
        assert get_custom_data_period(test_date_2)


def test_get_rose_types_and_layouts():
    test1_roses, test1_layouts = get_rose_types_and_layouts(False, False, False, False, False)
    test2_roses, test2_layouts = get_rose_types_and_layouts(True, False, True, False, True)
    test3_roses, test3_layouts = get_rose_types_and_layouts(True, True, True, True, True)

    assert test1_roses == [['default'], ['season', 'daylight'], ['month'], ['season'], ['daylight']]
    assert test1_layouts == [[1, 1], [4, 2], [3, 4], [2, 2], [2, 1]]
    assert test2_roses == [['default'], ['season', 'daylight'], ['daylight']]
    assert test2_layouts == [[1, 1], [4, 2], [2, 1]]
    assert test3_roses == [['default'], ['season'], ['season', 'daylight'], ['month'], ['daylight']]
    assert test3_layouts == [[1, 1], [2, 2], [4, 2], [3, 4], [2, 1]]


def test_slice_by_custom_dates():
    wss = range(240)
    wds = range(240)
    dates = pd.date_range(start=pd.to_datetime("2020/01/31"), freq='1H', periods=240)
    test_df = pd.DataFrame({"ws":wss, "wd":wds, "date":dates}, index=range(240))
    
    # Valid dates
    data_period = "1/2/2020-3/2/2020"
    test_wind_df_valid = slice_by_custom_dates(test_df, data_period)
    first_hour = test_wind_df_valid["date"].iloc[0]
    last_hour = test_wind_df_valid["date"].iloc[-1]
    assert first_hour == pd.to_datetime("1/2/2020", dayfirst=True)
    assert last_hour == pd.to_datetime("3/2/2020 23:00", dayfirst=True)
    
    # Invalid dates
    invalid_data_period = "1/1/2019-3/2/2019"
    with pytest.raises(ValueError):
        assert slice_by_custom_dates(test_df, invalid_data_period)


def test_parse_custom_hours():
    test1 = "1-6"
    test2 = "2,4,6,8"
    test3 = "1-5, 14-18"
    test4 = "1,2,3, 6-12, 22, 23"
    test1_hour_list = parse_custom_hours(test1)
    test2_hour_list = parse_custom_hours(test2)
    test3_hour_list = parse_custom_hours(test3)
    test4_hour_list = parse_custom_hours(test4)
    assert test1_hour_list == [1,2,3,4,5,6]
    assert test2_hour_list == [2,4,6,8]
    assert test3_hour_list == [1,2,3,4,5,14,15,16,17,18]
    assert test4_hour_list == [1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 22, 23]


def test_filter_df_by_hours():
    wss = range(24)
    wds = range(24)
    dates = pd.date_range(start=pd.to_datetime("2020/01/31"), freq='1H', periods=24)
    test_df = pd.DataFrame({"ws":wss, "wd":wds, "date":dates}, index=range(24))
    hours = [0,1,2,3,7,9]
    test_df = filter_df_by_hours(test_df, hours)
    assert len(test_df) == len(hours)


def test_slice_by_custom_hours():
    wss = range(24)
    wds = range(24)
    dates = pd.date_range(start=pd.to_datetime("2020/01/31"), freq='1H', periods=24)
    test_df = pd.DataFrame({"ws":wss, "wd":wds, "date":dates}, index=range(24))
    test1 = "1-6"
    test1_df = slice_by_custom_hours(test_df, test1)
    assert len(test1_df) == 6


def test_generate_annual_wind_dict():
    # 3-year dataframe for testing
    wss = range(26280)
    wds = range(26280)

    # Dataframe covering 3 years
    dates1 = pd.date_range(start=pd.to_datetime("2017/01/01"), freq='1H', periods=26280)
    test_df1 = pd.DataFrame({"ws": wss, "wd": wds, "date": dates1}, index=range(26280))
    test_dict1 = generate_annual_wind_dict(test_df1)
    years = list(test_dict1.keys())
    assert len(test_dict1) == 3
    assert years == [2017,2018,2019]

    # dataframe spanning over 4 years (2 incomplete)
    dates2 = pd.date_range(start=pd.to_datetime("2017/06/01"), freq='1H', periods=26280)
    test_df2 = pd.DataFrame({"ws": wss, "wd": wds, "date": dates2}, index=range(26280))
    test_dict2 = generate_annual_wind_dict(test_df2)
    years = list(test_dict2.keys())
    assert len(test_dict2) == 4
    assert years == [2017,2018,2019,2020]


def test_windrose_data_not_empty():
    # empty dataframe
    empty = pd.DataFrame({"ws": [], "wd": [], "date": []}, index=[])
    assert windrose_data_not_empty(empty, False) == False
    with pytest.raises(ValueError):
        assert windrose_data_not_empty(empty, True)

    # non-empty frame
    not_empty = pd.DataFrame({"ws": [1,2], "wd": [1,2], "date": [1,2]}, index=[0,1])
    assert windrose_data_not_empty(not_empty, False) == True

    # non-empty frame 2
    not_empty2 = pd.DataFrame({"ws": [1,-999], "wd": [1,-999], "date": [1,2]}, index=[0,1])
    assert windrose_data_not_empty(not_empty2, False) == True

    # non-empty frame containing null wd values
    not_empty_null_wd = pd.DataFrame({"ws": [1,2], "wd": [-999,-999], "date": [1,2]}, index=[0,1])
    assert windrose_data_not_empty(not_empty_null_wd, False) == False

    # non-empty frame containing null wd values
    not_empty_null_ws = pd.DataFrame({"ws": [-999,-999], "wd": [1,2], "date": [1,2]}, index=[0,1])
    assert windrose_data_not_empty(not_empty_null_ws, False) == False


def test_import_csv_data():
    # valid csv file
    file = r"E:\Misc\JW_Python\windroses_openair\Alphington_Nov_20.csv"
    header_lines = 1
    start_date = "1/11/2020"
    start_hour = 0
    num_hours = 720
    ws_col = "l"
    wd_col = "j"
    data = import_csv_data(file, header_lines, start_date, start_hour, num_hours, ws_col, wd_col)
    assert isinstance(data, pd.DataFrame)
    assert len(data) == 720

    # invalid csv with wrong number of hours specified
    num_hours = 721
    with pytest.raises(ValueError):
        assert import_csv_data(file, header_lines, start_date, start_hour, num_hours, ws_col, wd_col)

    # invalid csv with wrong date format
    start_date = "1-1-19"
    num_hours = 720
    with pytest.raises(ValueError):
        assert import_csv_data(file, header_lines, start_date, start_hour, num_hours, ws_col, wd_col)


# More tests to follow