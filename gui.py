from gooey import Gooey, GooeyParser

default_hours = '0-23'
default_ws_cats = '0.5,1,2,3,4,5,7,10,15,20'
default_grid = 10
default_ray = 30
default_calms = 0.5


@Gooey(default_size=(1200,900),required_cols=4, optional_cols=4, program_name="Met data wind rose and chart maker",
       clear_before_run=True,
       image_dir=r'\\auntl1fp001/Groups/!ENV/Team_AQ/Modelling/+Support_Data/+BOM Data')
def parse_args():
    # create GUI with input widgets
    prog_descrip = "Create wind roses from AECOM's met databases or selected csv file\n"
                   # "Create climate average charts (BoM data only)"
    parser = GooeyParser(description=prog_descrip)
    sub_parsers = parser.add_subparsers(help='commands', dest='command')

    #############################################################################################################################################

    database_tab = sub_parsers.add_parser('BoM_OEH_DES_EPAV_Station', help="Use this function to load data from AECOM's met DB")

    station_grp = database_tab.add_argument_group("Station details", "These parameters are required",
                                                  gooey_options={"show_border": True, "columns": 5})
    station_grp.add_argument('data_source', metavar='Data Source', widget='Dropdown', choices=['BOM', 'DES', 'OEH', 'EPAV'])
    station_grp.add_argument('station_id', metavar="Station ID", help='BoM station number without leading zeros or site name', type=str)
    station_grp.add_argument('output_folder', metavar="Output folder", help='Specify folder location to store output', type=str,
                              widget="DirChooser")
    station_grp.add_argument('latitude', metavar="Latitude", help='Latitude of station in degrees, e.g. -27', type=float, default=-34)
    station_grp.add_argument('longitude', metavar="Longitude", help='Longitude of station in degrees, e.g. 153', type=float, default=151)

    date_options_grp = database_tab.add_argument_group("Date options", "Select an optional date range an/or subset of hours",
                                                       gooey_options={"show_border": True, "columns": 2})
    date_options_grp.add_argument('--data_period', metavar="Data period", help="Optional start and end date e.g. 1/1/2019-31/12/2019", type=str)
    date_options_grp.add_argument('--cust_hours', metavar="Selected hours", help="Subset of hours or hour range e.g. 15 or 0-13 or 0-6,18-23",
                                  type=str, default=default_hours)

    wr_options_grp = database_tab.add_argument_group("Wind rose options", "Customise the wind roses",
                                                     gooey_options={"show_border": True, "columns": 6})
    wr_options_grp.add_argument('--wind_speed_categories', metavar="WS categories",
                              help="Custom wind speed categories - e.g. 0.5,1,3,5,7",
                              type=str, default=default_ws_cats)
    wr_options_grp.add_argument('--grid_spacing', metavar="Grid spacing", help="Custom frequency grid - e.g. 5 for 5% grids",
                              type=int, default=default_grid)
    wr_options_grp.add_argument('--ray_angle', metavar="Ray angle",
                              help="Angle for direction rays - e.g. 45 for an 8-ray wind rose",
                              type=float, default=default_ray)
    wr_options_grp.add_argument('--calms_threshold', metavar="Calms threshold (m/s)", help="Speed threshold for calms - e.g 0.2 - "
                                                        "should match minimum wind speed category",
                                type=float, default=default_calms)
    wr_options_grp.add_argument('--max_freq', metavar="Max freq", help="Max frequency circle - e.g. 40 - "
                                                 "default is automatic", type=int)
    wr_options_grp.add_argument('--prefix', metavar="Prefix", help="Enter an optional text prefix for wind rose outputs", type=str)

    bom_outputs_grp = database_tab.add_argument_group("Output wind rose selection", "Select the output wind roses to be generated"
                                                                  "- all will be generated (except the annual option) if no selections are made",
                                                   gooey_options={"show_border": True, "columns": 5})
    bom_outputs_grp.add_argument('--all_hours', metavar="All hours", widget="CheckBox", action="store_true")
    bom_outputs_grp.add_argument('--seasons', metavar="Seasons", widget="CheckBox", action="store_true")
    bom_outputs_grp.add_argument('--seasons_daylight', metavar="Seasons by daylight/night", widget="CheckBox", action="store_true")
    bom_outputs_grp.add_argument('--monthly', metavar="Monthly", widget="CheckBox", action="store_true")
    bom_outputs_grp.add_argument('--annual_daylight', metavar="Annual by daylight/night", widget="CheckBox", action="store_true")
    bom_outputs_grp.add_argument('--annual', metavar="Yearly", help="Select this to output wind roses for each selected year",
                                 widget="CheckBox", action="store_true")
    bom_outputs_grp.add_argument('--transparent', metavar='Save transparent images',
                             help='This will save transparent versions of all wind roses in addition to the default opaque versions',
                             action='store_true')

    #############################################################################################################################################

    csv_tab = sub_parsers.add_parser('csv', help="Use this function to load data from miscellaneous met data")

    inputs_grp = csv_tab.add_argument_group("CSV file parameters", gooey_options={"show_border": True, "columns": 5})
    inputs_grp.add_argument('csv_file', metavar="CSV file", help='Select file to load data from', widget='FileChooser')
    inputs_grp.add_argument('header_lines', metavar="Header lines", help='Number of header lines in csv', type=int)
    inputs_grp.add_argument('start_date', metavar="Start date", help='Enter the start date - e.g. 1/1/2019', type=str)
    inputs_grp.add_argument('start_hour', metavar="Start hour", help='Enter the start hour in 24-hour format - e.g. 0', type=int, default=0)
    inputs_grp.add_argument('num_hours', metavar="Num hours", help='Number of hours in file - e.g. 8760', type=int)
    inputs_grp.add_argument('WS_column', metavar="WS column", help='Wind speed column e.g. A',type=str)
    inputs_grp.add_argument('WD_column', metavar="WD column", help='Wind direction column', type=str)
    inputs_grp.add_argument('latitude', metavar="Latitude", help='Latitude of station in degrees, e.g. -27', type=float)
    inputs_grp.add_argument('longitude', metavar="Longitude", help='Longitude of station in degrees, e.g. 153', type=float)
    inputs_grp.add_argument('prefix', metavar="Prefix", help="Text prefix for wind rose image outputs", type=str)

    wr_grp = csv_tab.add_argument_group("CSV file parameters", gooey_options={"show_border": True, "columns": 4})
    wr_grp.add_argument('--data_period', metavar="Data period", help="Optional start and end date e.g. 1/1/2019-31/12/2019", type=str)
    wr_grp.add_argument('--cust_hours', metavar="Selected hours", help="Optional hour or hour range e.g. 15 or 0-13 or 0-6,18-23",
                        type=str, default=default_hours)
    wr_grp.add_argument('--wind_speed_categories', metavar="WS categories",
                              help="Custom wind speed categories - e.g. 0.5,1,3,5,7",
                              type=str, default=default_ws_cats)
    wr_grp.add_argument('--grid_spacing', metavar="Grid spacing", help="Custom frequency grid - e.g. 5 for 5% grids - default is 10",
                              type=int, default=default_grid)
    wr_grp.add_argument('--ray_angle', metavar="Ray angle",
                              help="Angle for direction rays - e.g. 45 fore an 8-ray wind rose - default is 30",
                              type=float, default=default_ray)
    wr_grp.add_argument('--calms_threshold', metavar="Calms threshold", help="Speed threshold for calms - e.g 0.2 - default is 0.5 - "
                                                        "should match min wind speed category", type=float, default=default_calms)
    wr_grp.add_argument('--max_freq', metavar="Max freq", help="Max frequency circle - e.g. 40 - "
                                                 "default is automatic", type=int)
    wr_grp.add_argument('--output_folder', metavar="Output folder", help='Specify optional output folder - default is same location as csv file', type=str,
                               widget="DirChooser")

    outputs_grp = csv_tab.add_argument_group("Output wind rose selection", "Select the output wind roses to be generated"
                                                              "- all will be generated (except the annual option) if no selections are made",
                                                   gooey_options={"show_border": True, "columns": 5})
    outputs_grp.add_argument('--all_hours', widget="CheckBox", action="store_true")
    outputs_grp.add_argument('--seasons', widget="CheckBox", action="store_true")
    outputs_grp.add_argument('--seasons_daylight', widget="CheckBox", action="store_true")
    outputs_grp.add_argument('--monthly', widget="CheckBox", action="store_true")
    outputs_grp.add_argument('--annual_daylight', metavar="Annual by daylight/night", widget="CheckBox", action="store_true")
    outputs_grp.add_argument('--annual', metavar="Yearly", help="Select this to output wind roses for each selected year",
                                 widget="CheckBox", action="store_true")
    outputs_grp.add_argument('--transparent', metavar='Save transparent images',
                             help='This will save transparent versions of all wind roses in addition to the default opaque versions',
                             action='store_true')

    args = parser.parse_args()
    return args