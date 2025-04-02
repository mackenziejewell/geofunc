# Functions for geographic analysis

# DEPENDENCIES:
import xarray as xr
import numpy as np
import numpy.ma as ma

import cartopy
import cartopy.crs as ccrs


from datetime import datetime, timedelta

from metpy.units import units

import pyproj 

# FUNCTIONS:
#---------------------------------------------------------------------
def project_vectors(projection, lon, lat, eastward = 1*units('m/s'), northward = 1*units('m/s'), final_units = 'm/day'):

    """ Convert eastward, northward vector components to projected coordinate system
    INPUT:
    - projection: projection to get final vector coordinates in 
    - eastward: eastward velocity component (with units)
    - northward: northward velocity component (with units)
    - lon: starting lon of vector (tail)
    - lat: starting lat of vector (tail)
    - final_units: AS STRING, with slash used as in example, units to convert final vector components to (default: 'm/day')
         * Distance component should be meters to match most standard projections

    OUTPUT:
    - tail: (x, y) projected coordinates of vector tail
    - tip: (x, y) projected coordinates of vector tip
    - vec: (u, v) projected components of vector
    """
    
    # find vector speed and angle
    # theta defined CCW from eastward
    theta = vector_angle(eastward, northward)
    S = np.sqrt(eastward**2 + northward**2)
    
    # Define the bearing (in degrees) and the distance to travel (in meters)
    # bearing defined CW form northward
    #==================
    bearing = - (theta - 90 * units('degree'))

    dist_units = final_units.split('/')[0]
    time_units = final_units.split('/')[1]

    distance = S.to(final_units) * units(time_units)    # dist traveled per desired time units
    #==================
    
    geod = pyproj.Geod(ellps='WGS84') # Create a Geod object
    
    # find ending lon, lat of vector (m traveled over a day)
    vlon, vlat, _ = geod.fwd(lon, lat, bearing, distance)
    
    # find coordinates of vector end point (tip)
    tipx_proj, tipy_proj = projection.transform_point(vlon, vlat, ccrs.PlateCarree())

    # find coordinates of vector start point (tail)
    tailx_proj, taily_proj = projection.transform_point(lon, lat, ccrs.PlateCarree())

    # find vector difference between start and end points
    # this assumes coordinates of projection are units
    u = np.array([tipx_proj - tailx_proj]) * units(final_units)
    v = np.array([tipy_proj - taily_proj]) * units(final_units)
    
    tail = (tailx_proj, taily_proj)
    tip = (tipx_proj, tipy_proj)
    vec = (u,v)
    
    return tail, tip, vec

def rotate_vector(u, v, angle):
    
    """Rotate vector [u,v] by angle (requires units)"""
    
    theta = angle.to('rad').magnitude
    
    ur = u * np.cos(theta) - v * np.sin(theta)
    vr = u * np.sin(theta) + v * np.cos(theta)
    
    return ur, vr

def dot_vectors(u1, v1, u2, v2):
    
    """Dot vectors [u1, v1] and [u2, v2]"""
    
    dot = (u1 * u2) + (v1 * v2)

    return dot

def comp_along_theta(u, v, angle):
    
    """Component of vector [u,v] along angle (requires units)"""
    
    theta = angle.to('rad').magnitude
    
    u1, v1 = u, v
    u2, v2 = np.cos(theta), np.sin(theta)
    
    dot = dot_vectors(u1, v1, u2, v2)

    return dot

def vector_angle(u, v):
    
    """Angle of vector [u,v]"""
    
    theta = np.arctan2(v, u)  * units('rad')

    return theta.to('deg')

def turning_angle(v1, v2):
    
    """Clockwise turning angle between vector v1=(x1,y1) and v2=(x2,y2)"""
    
    x1, y1 = v1
    x2, y2 = v2

    cross = x1*y2 - x2*y1
    dot = x1*x2 + y1*y2

    ta = - np.arctan2(cross, dot) * units('rad')

    return ta.to('deg')


def comp_along_vector(u1, v1, u2, v2):
    
    """Component of vector [u1, v1] along vector [u2, v2]"""

    dot = dot_vectors(u1, v1, u2, v2)

    mag2 = np.sqrt(u2**2 + v2**2)

    return dot / mag2
