from gui import parse_args
from functions import get_rose_types_and_layouts

if __name__ == "__main__":

    prog = parse_args()

    if prog.command == 'BoM_OEH_DES_EPAV_Station':
        from main_wind_rose_function import windrose_from_data

        rose_types, rose_layouts = get_rose_types_and_layouts(
            prog.all_hours,
            prog.seasons,
            prog.seasons_daylight,
            prog.monthly,
            prog.annual_daylight
        )

        windrose_from_data(
            data_source=prog.data_source,
            output_folder=prog.output_folder,
            lat=prog.latitude,
            long=prog.longitude,
            data_period=prog.data_period,
            selected_hours=prog.cust_hours,
            ws_categories=prog.wind_speed_categories,
            grid_spacing=prog.grid_spacing,
            ray_angle=prog.ray_angle,
            calms_threshold=prog.calms_threshold,
            max_freq=prog.max_freq,
            file_prefix=prog.prefix,
            rose_types=rose_types,
            rose_layouts=rose_layouts,
            annual=prog.annual,
            save_transparent=prog.transparent,
            database_source=True,
            station_id=prog.station_id
        )

    if prog.command == 'csv':
        from main_wind_rose_function import windrose_from_data

        rose_types, rose_layouts = get_rose_types_and_layouts(
            prog.all_hours,
            prog.seasons,
            prog.seasons_daylight,
            prog.monthly,
            prog.annual_daylight
        )

        windrose_from_data(
            data_source="csv",
            output_folder=prog.output_folder,
            lat=prog.latitude,
            long=prog.longitude,
            data_period=prog.data_period,
            selected_hours=prog.cust_hours,
            ws_categories=prog.wind_speed_categories,
            grid_spacing=prog.grid_spacing,
            ray_angle=prog.ray_angle,
            calms_threshold=prog.calms_threshold,
            max_freq=prog.max_freq,
            file_prefix=prog.prefix,
            rose_types=rose_types,
            rose_layouts=rose_layouts,
            annual=prog.annual,
            save_transparent=prog.transparent,
            database_source=False,
            csv_file=prog.csv_file,
            header_lines=prog.header_lines,
            start_date=prog.start_date,
            start_hour=prog.start_hour,
            num_hours=prog.num_hours,
            ws_col=prog.WS_column,
            wd_col=prog.WD_column,

        )

