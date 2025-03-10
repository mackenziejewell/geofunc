# General geopgraphic analysis


# DEPENDENCIES:
import xarray as xr
import numpy as np
import numpy.ma as ma

import cartopy
import cartopy.crs as ccrs

from metpy.units import units


# FUNCTIONS:
#---------------------------------------------------------------------

def coriolis(latitude):
    """ Calculate the Coriolis parameter for a given latitude
    INPUT:
    - latitude: latitude in degrees
    """

    omega = 7.2921e-5 * units('rad/s')  # earth's rotation rate
    f = 2 * omega * np.sin(np.deg2rad(latitude))
    
    return f