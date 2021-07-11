# Windrose-Tool-II
A Wind Rose Tool utilising a new Rpy2WindRose class to handle the generation of wind roses via R's Openair. This is a second generation, the first generation was simpler and did not utilise the Rpy2WindRose class.

The Rpy2WindRose class was developed to allow the simple generation of wind roses in python using R's openair package. The Rpy2WindRose class is based on the existing Rpy2 package and requires installation of R and Openair for the user and requires an R_HOME environment variable to be declared, as detailed in Rpy2's documentation. A range of wind rose types and other graphical options (see Openair documentation for guidance) are built into the Rpy2WindRose class. 

The Wind Rose Tool (WRT) itself is based around the Rpy2WindRose class and is specific to personal databases of meteorological data. This can be altered via parameters in the __params__ file to suit other databases, or changed completely to a SQL database or similar as required. 

Data can be input via the databases specified in the paths in the __params__ file or via a single custom csv file containing wind data. Files area accessed from the databases via a file description csv that is contained in each database. 

The WRT uses the gooey package to create a simple GUI that allows easy selection of data and options.

Sample png outputs have been uploaded.

This is an ongoing project and new features may be added in the future. 
