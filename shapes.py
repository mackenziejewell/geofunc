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


def make_geographic_box(bound_lat=[70.5,78], bound_lon=[187,220], num_points = 10):
    
    """Create smooth geographic box that smoothly follows parallels and 
meridians between input corner coordinates.

INPUT: 
- bound_lat: [South, North] boundaries of box (default: [70.5,78])
- bound_lon: [West, East] boundaries of box (default: [187,220])
- num_points: extra points to add between longitude bounds to smooth curves (default: 10)

OUTPUT:
- box_lons: array of longitude values
- box_lats: array of latitude values

DEPENDENCIES:
import numpy as np, numpy.ma as ma

Latest recorded update:
03-31-2025
    """
    
    
    # check that BOUND_LAT, BOUND_LON were given with correct shape
    #*****************************************************
    assertation_print = f"bound_lat and bound_lon should have shape (1 x 2). "
    assert len(bound_lat)==2,assertation_print+f"Got bound_lat with length {len(bound_lat)}."
    assert len(bound_lon)==2,assertation_print+f"Got bound_lon with length {len(bound_lon)}."
    #*****************************************************

    
    # make smooth geographic box
    #---------------------------
    # initiate straight line along lon0 boundaries from lat0 to lat1
    box_lons = np.array([bound_lon[0],bound_lon[0]])
    box_lats = np.array([bound_lat[0],bound_lat[1]])
    
    # add num_points steps between lon0 and lon1 along lat1
    for ii in range(1,num_points+1):
        box_lons = np.append(box_lons, bound_lon[0]+(ii*(bound_lon[1]-bound_lon[0])/(num_points+1)))
        box_lats = np.append(box_lats, bound_lat[1])
        
    # add extra straight line along lon1 boundaries from lat1 to lat0
    box_lons = np.append(box_lons,bound_lon[1])
    box_lons = np.append(box_lons,bound_lon[1])
    box_lats = np.append(box_lats,bound_lat[1])
    box_lats = np.append(box_lats,bound_lat[0])
    
    # add num_points steps between lon1 and lon0 along lat0
    for ii in range(1,num_points+1):
        box_lons = np.append(box_lons, bound_lon[1]+(ii*(bound_lon[0]-bound_lon[1])/(num_points+1)))
        box_lats = np.append(box_lats,bound_lat[0])
        
    # close box at initial point
    box_lons = np.append(box_lons,bound_lon[0])
    box_lats = np.append(box_lats,bound_lat[0])
    
    return box_lons, box_lats