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



def lat_weighted_mean(data_grid, latgrid):
    
    """ Calculate latitude-weighted spatial mean of data grid (for data on regular lat, lon grid)
    INPUT:
    - data_grid: (M x N) array of data values
    - latgrid: (M x N) array of latitudes (degrees)
    OUTPUT:
    - weighted_mean: lat-weighted spatial mean of data_grid
    """

    lat_weights = np.cos(latgrid*np.pi/180)
    
    weighted_mean = np.sum(lat_weights*data_grid) / np.sum(lat_weights)
    
    return weighted_mean