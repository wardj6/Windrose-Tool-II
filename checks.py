def raise_error(message, error):
    print(f"\n********** ERROR ********** {message}\n")
    raise error


def check_calms_threshold(cat_thresh, calms_thresh):
    if cat_thresh != calms_thresh:
        raise_error(f"Calms threshold of {calms_thresh} m/s does not match the minimum wind speed category of {cat_thresh} m/s",
                    ValueError)


def check_custom_inputs(input_type, input_val):
    check_dict = {"grid_spacing": [1, 101], "ray_angle": [10, 91], "max_freq": [5, 101], "header_lines": [1, 101]}
    c_input = check_dict.get(input_type)
    if input_val not in range(c_input[0],c_input[1]):
        raise_error(f"Custom {input_type} not valid - must be in the range {c_input[0]} to {c_input[1]-1}", ValueError)


def check_lat_long(lat, long):
    if lat not in range(-90,90):
        raise_error("latitude is invalid - must be in range -90 to 90", ValueError)
    if long not in range(-180,180):
        raise_error("longitude is invalid - must be in range -180 to 180", ValueError)


def check_and_get_ws_cat(cat):
    try:
        categories = cat.split(',')
        categories = [float(x.strip()) for x in categories]
    except:
        raise_error("Wind speed categories invalid - must be a list of numbers separated by commas", ValueError)
    else:
        return categories

