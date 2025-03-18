# General geopgraphic analysis


# DEPENDENCIES:
import xarray as xr
import numpy as np
import numpy.ma as ma

import cartopy
import cartopy.crs as ccrs

from pyproj import Geod
from shapely import wkt

from metpy.units import units


# FUNCTIONS:
#---------------------------------------------------------------------
def make_polygon(perim_coords, ellipsoid = "WGS84", quiet = True):
    
    """Create shapely polygon from coordinates of desired polygon perimeter.
    
INPUT:
- perim_coords: Nx2 array of (lon, lat) coords, where N > 2. 
  (e.g. np.array([[-140,70], [-150, 75], [-145, 72]]))
  * There is no need to 'close' the polygon by repeating the final coordinate
  
- ellipsoid: named ellipsoid used to create polygon 
  (default: "WGS84")
  
- quiet: bool True/False, whether or not to suppress print statements as function runs 
  (default: True)

OUTPUT:
- poly: Shapely polygon

DEPENDENCIES:
import numpy as np, numpy.ma as ma
from pyproj import Geod
from shapely import wkt

Latest recorded update:
06-23-2023
    """
    
    
    # check that perim_coords was given with correct shape
    #*****************************************************
    assertation_print = f"perim_coords should have shape (N x 2), where N>2. "
    # shoul be two dimensional array
    assert len(np.shape(perim_coords))==2,assertation_print+f"Expected 2-d array, got {len(np.shape(perim_coords))}-dimensional array."
    # should be at least 3 points in array to make polygon
    assert np.shape(perim_coords)[0]>=3, assertation_print+f"Got ({np.shape(perim_coords)[0]} x {np.shape(perim_coords)[1]})"
    #*****************************************************
    

    # make polygon
    #-------------
    # specify a named ellipsoid
    geod = Geod(ellps=ellipsoid)
    
    # check whether polygon is already closed with given coordinates
    if perim_coords[0][0] == perim_coords[-1][0] and perim_coords[0][1] == perim_coords[-1][1]:
        perim_coords = perim_coords[0:-1]
    
    # run through coordinates and add to polygon
    WKT_STR = 'POLYGON (('
    for ii in range(len(perim_coords)):
        WKT_STR=WKT_STR+f'{str(perim_coords[ii,:][0])} {str(perim_coords[ii,:][1])},'
    # close polygon by repeating first coordinate
    WKT_STR=WKT_STR+f'{str(perim_coords[0,:][0])} {str(perim_coords[0,:][1])}))'

    # generate polygon
    poly = wkt.loads(WKT_STR)
        
    if not quiet:
        print(f'--> created: {WKT_STR}')
        area = abs(geod.geometry_area_perimeter(poly)[0])
        print('--> Geodesic area: {:12.1f} sq. m'.format(area))
        print('-->                {:12.1f} sq. km'.format(area/1e6))
    
    return poly
