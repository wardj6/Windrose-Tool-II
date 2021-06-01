import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
from rpy2.rinterface_lib.callbacks import logger


class Rpy2WindRose:
    """
    Class to create windrose objects - each initial instance of a wind rose object will contain a pandas dataframe of date,
    wind speed and wind direction to plot in R's Openair.

    Attributes:
        data: pandas.DataFrame
            A dataframe containing three columns 'date', 'ws' and 'wd' - these columns are used to generate an R dataframe via RPY2
            No default, must be passed to WindRose() function
        latitude: float
            The latitude of the station - used to partition daytime and night-time hours in the wind roses
            Openair arg = 'lat'
            Default = -34 (Sydney)
        longitude: float
            The longitude of the station - used to partition daytime and night-time hours in the wind roses
            Openair arg = 'long'
            Default = 151 (Sydney)
        station: string
            The name or ID of the station
            Default = 'station'
        categories: list
            A list of wind speed categories that's used to bin the wind speeds
            Openair arg = 'breaks'
            Default = [0.5, 1, 2, 3, 4, 5, 7, 10, 15, 20]
        grid: int
            The grid line interval
            Openair arg = 'grid.line'
            Default = 10
        ray_angle:
            The angle between rays of the wind rose
            Openair arg = 'angle'
            Default = 30
        max_frequency: int (or str as default)
            Controls the scaling of the radial limits
            Openair arg = 'max.freq'
            Default = 'Null'
        rose_type: list
            A 1-dimensional or 2-dimensional list of strings that contain the type of wind rose to be generated
            Openair arg = 'type'
            Default = ['default']
        rose_layout: list
            A 2-dimensional list of integers [num columns, num rows] that controls the layout of the wind roses
            Openair arg = 'layout'
            Default = [1,1]
        year_string: string
            Used to append to output file name to denote a specfic annual wind rose when outputting a specified year
            Default = ''
        png_file_path: pathlib Path object or string
            The path and file name for where to save the generated wind rose figure
            Default = 'wind_rose.png'
        width: int
            The specified width of the output wind rose in pixels
            Default = 1000
        height: int
            The height of the output wind rose in pixels
            Default = 1000
        paddle: Bool
            Whether to display the wind rose as paddle style or not
            Openari arg = 'paddle'
            Default = False
        key_position: string
            Location for the wind speed key
            Openair arg = 'key.position'
        fontsize: int
            Size of font in figure
            Openair arg = 'fontsize'
            Default = 25
        colours: string
            The colour scheme to use for the windroses
            Openair arg = 'cols'
            Default = 'default'
        offset: int
            The size of the 'hole' in the middle of the wind rose
            Openair arg = 'offset'
            Default = 10
        hemisphere: string
            Northern or southern hemisphere - used for handling the seasonal split of data for 'seasons' type wind roses
            Openair arg = 'hemisphere'
            Default = 'southern'
        border: string
            The border colour for shaded areas
            Openair arg = 'border'
            Default = 'black'
        seg: float:
            The width of the wind rose ray segments
            Openair arg = 'seg'
            Default = 0.6
        suppress_r_warnings: Bool
            Suppress warnings from R in console
            Default = True
        base: R 'base' package
             The 'base' package is imported on initialisation of an Rpy2WindRose object
        grdevices: R 'grDevices' package
            The 'grDevices' package is imported on initialisation of an Rpy2WindRose object
        openair: R 'openair' package
            The 'openair' package is imported on initialisation of an Rpy2WindRose object
            Note that the openair package must be installed for the user's instance of R

    Functions:
        prepare_r(self) -> None
            Import RPY2 packages, converts class variables to R-style and opens and returns R objects that are used for generating the wind roses
        create_wind_rose(self) -> None
            Generates the wind rose  and saves it as a PNG file to the specified path location in 'self.png_file_path'
    """

    def __init__(self, data):
        """
        Generates an instance of the class WindRose with default variables that will be converted to R openair windrose settings
        :param data: a pandas dataframe object with 3 columns - 'date', 'ws', 'wd'
        """
        self.data = data
        self.latitude = -34
        self.longitude = 151
        self.station = 'station'
        self.categories = [0.5, 1, 2, 3, 4, 5, 7, 10, 15, 20]
        self.grid = 10
        self.ray_angle = 30
        self.max_frequency = "Null"
        self.rose_type = ["default"]
        self.rose_layout = [1,2]
        self.year_string = ""
        self.png_file_path = "wind_rose.png"
        self.image_name = ""
        self.width = 1000
        self.height = 1000
        self.paddle = False
        self.key_position = "right"
        self.fontsize = 25
        self.colours = "default"
        self.offset = 10
        self.hemisphere = "southern"
        self.border = "black"
        self.seg = 0.6
        self.suppress_r_warnings = True
        self.base = importr("base")
        self.grdevices = importr("grDevices")
        self.openair = importr("openair")

    def prepare_r(self):
        """
        Converts class variables to R-style and opens and returns R objects that are used for generating the wind roses
        Pandas dataframe is converted to R dataframe
        :return: three R packages - openair, grdevices and base
        """
        if self.suppress_r_warnings:
            import logging
            logger.setLevel(logging.ERROR)

        if type(self.categories) is list:
            self.categories = ro.FloatVector(self.categories)

        if self.max_frequency == "NULL":
            self.max_frequency = ro.NULL

        pandas2ri.activate()

        with localconverter(ro.default_converter + pandas2ri.converter):
            self.data = ro.conversion.py2rpy(self.data)

    def create_wind_rose(self):
        """
        This function generates the wind rose and saves it as a PNG file to path specified in self.png_file_path
        """

        self.prepare_r()

        if len(self.rose_type) == 1:
            r_type = self.base.c(self.rose_type[0])
        else:
            r_type = self.base.c(self.rose_type[0], self.rose_type[1])

        self.grdevices.png(file=str(self.png_file_path), width=self.width, height=self.height)

        self.openair.windRose(mydata=self.data,
                              type=r_type,
                              hemisphere=self.hemisphere,
                              layout=self.base.c(self.rose_layout[0], self.rose_layout[1]),
                              border=self.border,
                              angle=self.ray_angle,
                              cols=self.colours,
                              breaks=self.categories,
                              paddle=str(self.paddle),
                              offset=self.offset,
                              key_position=self.key_position,
                              fontsize=self.fontsize,
                              grid_line=self.grid,
                              max_freq=self.max_frequency,
                              seg=self.seg
                              )

        self.grdevices.dev_off()
