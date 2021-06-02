import math
from pathlib import Path
from __params__ import data_source_dict, r_type_size_dict
from checks import check_lat_long, check_custom_inputs, check_calms_threshold, check_and_get_ws_cat
from functions import import_data, get_data_source, create_new_folder_for_output, \
    slice_by_custom_dates, slice_by_custom_hours, generate_annual_wind_dict, make_image_transparent, \
    replace_calms, windrose_data_not_empty, import_csv_data, update_output_path
from rpy2_windrose import Rpy2WindRose


def windrose_from_data(
        data_source,
        output_folder,
        lat,
        long,
        data_period,
        selected_hours,
        ws_categories,
        grid_spacing,
        ray_angle,
        calms_threshold,
        max_freq,
        file_prefix,
        rose_types,
        rose_layouts,
        annual,
        save_transparent,
        **kwargs
):
    """
    Main function that creates an rpy2WindRose object for each user selected wind rose type to generate. All wind rose data processing is controlled from this function
    :param data_source: Database identifier - string
    :param output_folder: path to wind rose output location
    :param lat: latitude of station
    :param long: longitude of station
    :param data_period: optional data period to slice the wind data
    :param selected_hours: Subset of hours to slice the wind data
    :param ws_categories: WS categories to display in wind rose
    :param grid_spacing: grid spacing format in wind rose
    :param ray_angle: angle of rays in wind roses
    :param calms_threshold: threshold for calm winds in m/s
    :param max_freq: maximum radial axis limit in wind roses
    :param file_prefix: prefix to append to files for saving
    :param rose_types: list of types of openair roses to be generated
    :param rose_layouts: list of layouts to accompany each rose type
    :param annual: controls whether to output annual wind roses or not
    :param save_transparent: controls whether to save transparent version of the default all-data wind roses
    :return: None
    """

    station_id = kwargs.get("station_id", "")

    # Perform checks on inputs upfront
    check_lat_long(lat, long)
    check_custom_inputs("grid_spacing", grid_spacing)
    check_custom_inputs("ray_angle", int(math.floor(ray_angle)))
    ws_categories = check_and_get_ws_cat(ws_categories)
    check_calms_threshold(ws_categories[0], calms_threshold)
    if max_freq or max_freq == 0:
        check_custom_inputs("max_freq", max_freq)
    else:
        max_freq = "NULL"

    if kwargs.get("database_source"):
        # Data is located in one of AECOM's databases
        data_location = data_source_dict.get(data_source)
        data_file = get_data_source(data_source, data_location, station_id)
        new_output_folder = Path(create_new_folder_for_output(output_folder, station_id))
        wind_df = import_data(data_source, data_file)
    else:
        # Data is via custom CSV file
        data_file = Path(kwargs.get("csv_file"))
        if output_folder:
            new_output_folder = Path(output_folder)
        else:
            new_output_folder = Path(data_file).parent
        wind_df = import_csv_data(data_file, kwargs.get("header_lines"), kwargs.get("start_date"), kwargs.get("start_hour"),
                                  kwargs.get("num_hours"), kwargs.get("ws_col"), kwargs.get("wd_col"))

    wind_df = slice_by_custom_dates(wind_df, data_period)
    wind_df = slice_by_custom_hours(wind_df, selected_hours)
    wind_df = replace_calms(wind_df, calms_threshold)

    if windrose_data_not_empty(wind_df, True):

        if file_prefix:
            station_id = file_prefix + "_" + station_id

        annual_wind_dict = {}
        if annual:
            annual_wind_dict = generate_annual_wind_dict(wind_df)

        for r_type, layout in zip(rose_types, rose_layouts):
            wind_rose = Rpy2WindRose(data=wind_df)
            wind_rose.latitude = lat
            wind_rose.longitude = long
            wind_rose.station = station_id
            wind_rose.categories = ws_categories
            wind_rose.grid = grid_spacing
            wind_rose.ray_angle = ray_angle
            wind_rose.max_frequency = max_freq
            wind_rose.rose_type = r_type
            wind_rose.rose_layout = layout
            wind_rose.width = r_type_size_dict.get("_".join(r_type))[0]
            wind_rose.height = r_type_size_dict.get("_".join(r_type))[1]
            wind_rose.year_string = 'all_data'

            wind_rose.png_file_path = update_output_path(new_output_folder, wind_rose.station, wind_rose.rose_type, wind_rose.year_string)

            wind_rose.create_wind_rose()
            print("\nGenerated " + "_".join(wind_rose.rose_type) + " windrose\n")

            images = [wind_rose.png_file_path]

            for year, wind_data in annual_wind_dict.items():
                if windrose_data_not_empty(wind_data, False):
                    print(f"Generating wind rose for {year}")
                    wind_rose.data = wind_data
                    wind_rose.year_string = str(year)
                    wind_rose.png_file_path = update_output_path(new_output_folder, wind_rose.station, wind_rose.rose_type, wind_rose.year_string)
                    wind_rose.create_wind_rose()
                    images.append(wind_rose.png_file_path)

            if save_transparent:
                for image in images:
                    if "default" in image:  # only default 'all-hours' wind roses are saved as transparent versions
                        make_image_transparent(image)

