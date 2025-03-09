# Functions for plotting geographic data

# DEPENDENCIES:
import xarray as xr
import numpy as np
import numpy.ma as ma

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeat

import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors
from matplotlib.offsetbox import AnchoredText
import matplotlib.patches as patches
import cmocean

from datetime import datetime, timedelta
from metpy.units import units
from shapely import wkt


# FUNCTIONS:
#---------------------------------------------------------------------
def fix_cartopy_vectors(u, v, uvlats):
    
    """Function to output vector components for plotting in cartopy. 
    
    Reads in vectors and associated latitudes, return fixed vectors. 
    
    Cartopy doesn't know meters per degree increase toward the pole 
    in zonal direction as cosine(lat) when reprojecting for vectors 
    given as m/s (where  a meter covers different amount of a degree 
    depending on latitude), we need to rescale the u (east-west) speeds. 
    otherwise at high latitudes, u will be drawn much larger than 
    they should which will give incorrect angles

INPUT: 
- u: (N x M) array of eastward velocity component (m/s)
- v: (N x M) array of northward velocity component (m/s)
- uvlats: (N x M) array latitudes associated with u,v vectors

OUTPUT:
- u_fixed: (N x M) array of u with correct angle and magnitude for plotting
- v_fixed: (N x M) array of v with correct angle and magnitude for plotting

Latest recorded update:
12-17-2024
    """
    
    # FIX ANGLE
    # fix u scale to be correct relative to v scale
    #----------------------------------------------
    # for u (m/s), m/degree decreases as cos(lat)
    u_fixed = u/np.cos(uvlats/180*np.pi) 
    v_fixed = v  # v does not change with latitude

    # FIX MAGNITUDE
    # scale fixed u,v to have correct magnitude 
    #-----------------------
    # original magnitude 
    orig_mag = ma.sqrt(u**2+v**2)
    # new magnitude
    fixed_mag = ma.sqrt(u_fixed**2+v_fixed**2)
    u_fixed = u_fixed*(orig_mag/fixed_mag)
    v_fixed = v_fixed*(orig_mag/fixed_mag)

    return u_fixed, v_fixed

def land(ax, scale = '50m', color='gray', alpha=1, fill_dateline_gap = True, zorder=2):
    
    """Add land feature to cartopy figure
    
INPUT:
- ax: cartopy figure axis
- scale = NaturalEarthFeature land feature scale (e.g. '10m', '50m', '110m')
        (default: '50m')
- color = land color (e.g. 'k' or [0.9,0.6,0.5]) (default: 'gray')
- alpha = land opacity (default: 1)
- zorder: drawing order of land layer (default: 2)
- fill_dateline_gap: specify whether to fill gap in cartopy land feature along 
   dateline that crosses Russia and Wrangel Island (default: True)

Latest recorded update:
01-31-2025

    """
    
        
    # grab land from cfeat.NaturalEarthFeature
    #-----------------------------------------
    ax.add_feature(cfeat.NaturalEarthFeature(category='physical', name='land', 
                                             scale=scale, facecolor=color),
                                             alpha = alpha, zorder = zorder)

    # if specified, fill dateline gap in land feature with shapely polygons
    if fill_dateline_gap == True:
        # generate polygon to fill line across Wrangel Island and line across Russia
        WKT_fill_Wrangel = 'POLYGON ((-180.1 71.51,-180.1 71.01,-179.9 71.01,-179.9 71.51,-180.1 71.51))'
        poly1 = wkt.loads(WKT_fill_Wrangel)
        ax.add_geometries([poly1], crs=ccrs.PlateCarree(), 
              facecolor=color, edgecolor=color, alpha = alpha, zorder=zorder)
        WKT_fill_Russia = 'POLYGON ((-180.1 65.1,-180.1 68.96,-179.9 68.96,-179.9 65.1,-180.1 65.1))'
        poly2 = wkt.loads(WKT_fill_Russia)
        ax.add_geometries([poly2], crs=ccrs.PlateCarree(), 
              facecolor=color, edgecolor=color, alpha = alpha, zorder=zorder)

def coast(ax, scale = '50m', color='gray', linewidth = 1, alpha=1, zorder=3):

    """Add land feature to cartopy figure
    
INPUT:
- ax: cartopy figure axis
- scale = NaturalEarthFeature coast feature scale (e.g. '10m', '50m', '110m')
        (default: '50m')
- color = coastline color (e.g. 'k' or [0.9,0.6,0.5]) (default: 'gray')
- linewidth = coastline linewidth (default: 1)
- alpha = coastline opacity (default: 1)
- zorder: drawing order of coast layer (default: 3)

Latest recorded update:
01-31-2025

    """

    # coastline
    #----------
    ax.coastlines(scale, color=color, linewidth=linewidth, alpha = alpha, zorder = zorder)

def grid(ax, lats = None, lons = None, linewidth = 1, color = 'gray', alpha=0.5, zorder = 4): 
    
    """Add specified gridlines to cartopy figure.
    
INPUT:
- ax: cartopy figure axis
- lats: None or array of latitudes to plot lines (default: None)
- lons: None or array of latitudes to plot lines (default: None)
- linewdith: grid line linewidths (default: 1)
- color: grid line color (default: 'gray')
- alpha: line transparency (default: 0.5)
- zorder: drawing order of gridlines layer (default: 4)


Latest recorded update:
01-31-2025

    """
        
    # give gridline specifications
    #-----------------------------
    gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=linewidth, color=color, alpha=alpha, zorder = zorder)

    # add the longitude gridlines
    #----------------------------
    if lons is None:
        gl.xlocator = mticker.FixedLocator([])
    else:
        # shift all longitudes from [0,360] to [180,-180]
        lons = np.concatenate((lons[(lons>180)]-360,lons[(lons<=180)]))
        gl.xlocator = mticker.FixedLocator(lons)

        
    # add the latitude gridlines
    #----------------------------
    if lats is None:
        gl.ylocator = mticker.FixedLocator([])
    else:
        gl.ylocator = mticker.FixedLocator(lats)

def add_date(fig, ax, dt_obj, date_format = '%b %d, %Y (%H:%M UTC)', method = 'anchor',
             boxstyle="round,pad=0.,rounding_size=0.2", facecolor = 'black', edgecolor = 'black',
             zorder = 10,
             
             anchor_loc = 4, anchor_prop = {'size': 20, 'color':'white'},
             

             x = 0.02, y= 0.05, textcolor = 'white',fontsize=15): 
    
    """Add date label to cartopy plot.
    
INPUT:
- fig: cartopy figure
- ax: cartopy figure axis
- dt_obj: datetime object of date for plotted data 
            OR
          string with text to show (date format already provided (e.g. 'Dec 20, 2018 (6:00 UTC)')
          
IF dt_obj IS DATETIME OBJECT:
- date_format: str, format to display date (default: '%b %d, %Y (%H:%M UTC)')
    - example 1: '%b %d, %Y (%H:%M UTC)' could give 'Dec 20, 2018 (6:00 UTC)'
    - example 2: '%m-%d-%Y' could give '12-20-2018'
    
- method: method to place the date label (either 'anchor' for AnchoredText or 'manual' to place manually).
        (default: 'anchor')
- boxstyle: anchor box shape style (default: "round,pad=0.,rounding_size=0.2")
- facecolor: color of bounding box (default: 'black')
- edgecolor: color of bounding box edge (default: 'black')
- zorder: drawing order of date layer (default: 10)

IF METHOD = 'anchor':
- anchor_loc: anchor text location (default: 4)
- anchor_prop: anchor properties dictionary (default: {'size': 20, 'color':'white'})

IF METHOD = 'manual':
- x: x-location of figure extent to place date
- y: y-location of figure extent to place date
- textcolor: color oftext (default: 'white')
- fontsize: fontsize of text (defult: 15)

OUTPUT:
- input plot with added date label

Latest recorded update:
12-17-2024
    """

    
    assert method in ['anchor', 'manual'], f">>> method should be 'manual' or 'anchor', given: '{method}'"
    
    assert str(type(dt_obj)) in ["<class 'datetime.datetime'>", "<class 'str'>"], f">>> dt_obj should be datetime object or string, given: {str(type(dt_obj))}"
    
    
    # if given as datetime object, convert to specified date format
    if str(type(dt_obj)) == "<class 'datetime.datetime'>":
        date_text = dt_obj.strftime(date_format)
    
    # else, set date directly to given string object
    else:
        date_text = dt_obj
    
    
    # add text
    #---------
    if str(method) == 'anchor':
        at = AnchoredText(date_text, loc=anchor_loc, prop=anchor_prop)
        at.patch.set_boxstyle(boxstyle)
        at.patch.set_facecolor(facecolor)
        at.patch.set_edgecolor(edgecolor)
        at.zorder = zorder
        ax.add_artist(at)
    
    elif str(method) == 'manual':
        ax.text(x, y, date_text, 
                bbox=dict(boxstyle = boxstyle, facecolor=facecolor, edgecolor = edgecolor), 
                transform=ax.transAxes, fontsize=fontsize, 
                c=textcolor, verticalalignment='top', zorder = zorder);

def scalebar(ax, loc = (0.1, 0.1), stepsize = 50,  numsteps = 4, unit = 'km', 
             label = None,
             colors=['k','w'], edgecolor = None, textsize=9, lw = 1, bar_width = 0.025,
             labelpad = 0.015, ticklabelpad = 0.01, zorder=100):

    """Add scalebar to to cartopy plot.
    
INPUT:
- ax: cartopy figure axis
- loc = (x,y) of scalebar's lower left corner, in axes coordinates [0,1] (default: (0.1,0.1))
- stepsize: distance between scalebar ticks (default: 50)
- numsteps: number of scalebar ticks (default: 4)
- unit: unit of scalebar (default: 'km')
- label: unit label to display (if None, will use unit) (default: None)
- colors: list of 2 alternating colors for scalebar ticks (default: ['k','w'])
- lw: linewidth of scalebar edge (default: 1)
- bar_width: height of scalebar rectangle in axes coordinates [0,1] (default: 0.025)
- textsize: size of scalebar text (default: 9)
- labelpad: padding between unit label and scalebar (default: 0.025)
- ticklabelpad: padding between scalebar ticks and labels (default: 0.025)
- zorder: drawing order of scalebar layer (default: 100)

Latest recorded update:
01-31-2025
    """

    def axes_to_proj_units(x, y):
        # convert from Axes coordinates to display coordinates
        (xd, yd) = ax.transAxes.transform((x, y))
        # convert from display coordinates to data coordinates
        (x0, y0) = ax.transData.inverted().transform((xd, yd))
        return (x0, y0)

    # convert step size to m
    step_with_units = stepsize * units(unit)
    step = (step_with_units).to('m').magnitude

    # convert lower left corner of scalebar
    # from figure display coordinates to projected coordinates
    # follow: https://stackoverflow.com/questions/56662941/cartopy-convert-point-from-axes-coordinates-to-lat-lon-coordinates
    xi, yi = loc
    (x0, y0) = axes_to_proj_units(xi,yi)
    
    # scalebar width in proj coordinates
    (xxx, y2) = axes_to_proj_units(xi,yi+bar_width)
    dy = y2 - y0

    # top and bottom label locations
    # convert to axes coordinates
    # number labels
    (xxx, ticky) = axes_to_proj_units(xi,yi+ticklabelpad)
    ticky += dy # move up from top of scalebar

    # print(step_m)
    # figure_projection = ax.projection
    
    # rectangle size paramters
    width = step  # Width of the rectangle
    height = dy# step/6  # Height of the rectangle
    y = y0  # y-coordinate of the lower-left corner

    # determine color of scalebar edge
    linecolor = colors[0]
    if edgecolor is not None:
        linecolor = edgecolor
    
    # Create the scalebar (loop over each segment)
    for ii in range(numsteps+1):

        # Define rectangle position 
        x = x0 + (step*ii) # x-coordinate of the lower-left corner

        # label ticks
        dist_label = step_with_units.magnitude * ii
        dist = f'{dist_label}'
        ax.text(x, ticky, dist, va='bottom', ha = 'center', size=textsize, zorder=zorder)    

        if ii < numsteps:
            # draw the Rectangle patch
            rect = patches.Rectangle((x, y), width, height, 
                                     linewidth=lw, edgecolor=linecolor, facecolor=colors[ii%2], zorder=zorder)
            ax.add_patch(rect)

    # label units of scalebar
    # unit labels
    labelx = x0 + ((numsteps/2)*step)
    (xxx, labely) = axes_to_proj_units(xi,yi-labelpad)

    LABEL = unit
    if label is not None:
        LABEL = label
    
    ax.text(labelx, labely, LABEL, va='top', ha = 'center', size=textsize, zorder=zorder)
    
def northarrow(ax, loc = (0.1, 0.1), textsize=9,):

    """Add north arrow to to cartopy plot.
    
INPUT:
- ax: cartopy figure axis
- loc = (x,y) of arrow in axes coordinates [0,1] (default: (0.1,0.1))
- textsize: size of arrow label text (default: 9)

Latest recorded update:
01-30-2025
    """


    # convert desired arrow coordinates to projection
    # from figure display coordinates to projected coordinates
    # follow: https://stackoverflow.com/questions/56662941/cartopy-convert-point-from-axes-coordinates-to-lat-lon-coordinates
    xi, yi = loc
    # convert from Axes coordinates to display coordinates
    (xd, yd) = ax.transAxes.transform((xi, yi))
    # convert from display coordinates to data coordinates
    (x0, y0) = ax.transData.inverted().transform((xd, yd))

    # convert from data to cartesian coordinates
    proj_cart = ccrs.PlateCarree()
    (lon, lat) = proj_cart.transform_point(*(x0, y0), src_crs=ax.projection)

    # arrow_lon = -153.5
    # arrow_lat = 69.75
    
    ax.text(np.array([lon]), np.array([lat]), 'N', weight='bold', va = 'center', ha='center',
            size = textsize,    
             transform=ccrs.PlateCarree(), zorder=300)
    
    ax.quiver(np.array([lon]), np.array([lat+0.05]), 
                np.array([0]), np.array([1]), scale=28,
                width = 0.0005, 
                headaxislength = 650, headlength = 1000, headwidth=1000,
                transform=ccrs.PlateCarree(), zorder=300)
    
def map_alaska(map_projection = ccrs.NorthPolarStereo(central_longitude=-153), 
               location = 'fullshelf', figsize = (8,4), background_color = 'lightgray', 
               add_land = True,
                place_labels = False,
                oceantext_kwargs = {'color' : 'gray', 'alpha':1,  'weight':'normal',
                       'ha' : 'center', 'va':'center', 'zorder':11},
                landtext_kwargs = {'color' : 'k', 'alpha':1,  'weight':'normal',
                       'ha' : 'center', 'va':'center', 'zorder':11}):

    """Initiate standardized Alaska map plots.
    
INPUT:
- map_projection: cartopy projection to use (default: ccrs.NorthPolarStereo(central_longitude=-153))
- location: some default map ranges to use. (currently correspond only to NPS proj) (default: 'fullshelf')
    Options: ['fullshelf', 'west1', 'west2']
- figsize: figure size (default: (8,4))
- background_color: background color of map (default: 'lightgray')
- add_land: if True, add land feature to map (default: True)
- place_labels: if True, add place labels to map (default: True)
- oceantext_kwargs: dictionary of text properties for ocean labels
- landtext_kwargs: dictionary of text properties for land labels

OUTPUT:
- fig: cartopy figure
- ax: cartopy figure axis

Latest recorded update:
01-30-2025
    """

    allowed_locs = ['fullshelf', 'west1', 'west2']
    assert location in allowed_locs, f"location should be one of {allowed_locs}, given: {location}"

    fig, ax = plt.subplots(subplot_kw=dict(projection=map_projection), 
                           figsize=figsize)
    ax.set_facecolor(background_color)
    
    if add_land:
        land(ax, scale = '10m', color='gray', alpha=1, fill_dateline_gap = True, zorder=2)

    # map extent (right now range applies to NorthPolarStereo proj)
    if str(location) == 'fullshelf':
        ax.set_xlim(-310000,220000+400000)
        ax.set_ylim(-2310000,-1980000+8000)

    elif str(location) == 'west1':
        expand = 8000
        ax.set_xlim(-200000-expand,220000+expand)
        ax.set_ylim(-2270000-expand,-1980000+expand)

    elif str(location) == 'west2':
        expand = 8000
        ax.set_xlim(-200000-expand,420000+expand)
        ax.set_ylim(-2270000-expand,-1980000+expand)

    if place_labels:

        
        # ax.text(0.465,0.51,'Beaufort Shelf', rotation=-13, transform=ax.transAxes, **text_kwargs)
        # ax.text(0.5,0.485,'Alaskan Beaufort Shelf', rotation=-13, transform=ax.transAxes, **text_kwargs)
        
        ax.text(0.6,0.8,'Beaufort\nSea', rotation=0, size=12, transform=ax.transAxes, **oceantext_kwargs)
        ax.text(0.075,0.775,'Chukchi\nSea', rotation=0, size=10.5, transform=ax.transAxes, **oceantext_kwargs)

        ax.scatter(-156.7886, 71.2906, marker='*', c=landtext_kwargs['color'], s=100, lw=0, zorder=100, transform=ccrs.PlateCarree())
        # ax.text(0.145,0.55,'Point\nBarrow', rotation=0, size=9, transform=ax.transAxes, **text_kwargs)
        ax.text(0.137,0.55,'Utqiagvik', rotation=0, size=9, transform=ax.transAxes, **landtext_kwargs)

        ax.scatter(-148.4, 70.29, marker='*', c=landtext_kwargs['color'], s=100, lw=0, zorder=100, transform=ccrs.PlateCarree())
        ax.text(0.55,0.2,'Prudhoe Bay', rotation=0, size=9, transform=ax.transAxes, **landtext_kwargs)

    
    # if scalebar:
        
    #     scalebar(ax, corner = (0.1, 0.1), stepsize = 50,  numsteps = 4, unit = 'km', 
    #                      unit_label = 'Kilometers',
    #                      colors=['k','w'], textsize=9, lw = 3, 
    #                      unitpad = 0.025, labelpad = 0.025)
    #     northarrow(ax, loc = (0.15,0.25))


    return fig, ax 

    # ax.add_feature(cfeat.NaturalEarthFeature('physical', 'land', '10m', 
    #                                             edgecolor='face', facecolor='gray'), zorder=2)

def gebco_bathymetry(ax, 
                     file_path = '/Volumes/Seagate_Jewell/KenzieStuff/GEBCO/GEBCO_2024/gebco_2024_n90.0_s55.0_w-180.0_e180.0.nc',
                     crop_lat = (69, 72.5), crop_lon = (-170,-130), clat = 5, clon = 15,
                     depth_shade = True, 
                     shade_norm = matplotlib.colors.TwoSlopeNorm(-300, vmin=-3500, vmax=-5),
                     shade_cmap = cmocean.tools.crop_by_percent(cmocean.cm.deep_r, 20, which='min', N=None),
                     shade_zorder = 0,
                     depth_contours = True, 
                     contour_levels = [-100,-20],
                     contour_kwargs = {'colors': 'gray', 'linewidths': 1, 'linestyles': 'dashed', 'zorder':1},
                     contour_labels=True,
                     text_kwargs = {'size' : 10, 'color' : 'gray', 'weight':'normal', 'zorder':100},):
    
    """Add bathymetry to cartopy plot, various options.
    
INPUT:
- ax: cartopy figure axis
- file_path: path to GEBCO bathymetry file (default: '/Volumes/Seagate_Jewell/KenzieStuff/GEBCO/GEBCO_2024/gebco_2024_n90.0_s55.0_w-180.0_e180.0.nc')
- clat: coarsening factor for latitude (default: 5)
- clon: coarsening factor for longitude (default: 15)
- depth_shade: if True, shade bathymetry (default: True)
- shade_norm: shading colormap normalization (default: matplotlib.colors.TwoSlopeNorm(-300, vmin=-3500, vmax=-5))
- shade_cmap: shading colormap (default: cmocean.tools.crop_by_percent(cmocean.cm.deep_r, 20, which='min', N=None))
- shade_zorder: drawing order of shaded bathymetry layer (default: 0)
- depth_contours: if True, add bathymetry contours (default: True)
- contour_levels = levels of contours to plot (default: [-100,-20])
- contour_kwargs: dictionary of contour properties
- contour_labels: if True, add contour labels (default: True)
- text_kwargs: dictionary of text properties for contour labels

Latest recorded update:
01-31-2025
    """

    # import data and crop
    ds = xr.open_dataset(file_path)
    ds.close()
    lat_slice = slice(crop_lat[0], crop_lat[1])
    lon_slice = slice(crop_lon[0], crop_lon[1])
    dscrop = ds.sel(lat=lat_slice, lon=lon_slice)

    # coarsen resolution
    elongrid, elatgrid = np.meshgrid(dscrop.lon[::clon], dscrop.lat[::clat])
    elevations = dscrop.elevation.values[::clat, ::clon]


    if depth_shade:
        norm = shade_norm
        cmap = shade_cmap
        ax.pcolormesh(elongrid, elatgrid, elevations,
                    cmap=cmap, norm=norm,
                    zorder=shade_zorder, transform=ccrs.PlateCarree())
    if depth_contours:
        ax.contour(elongrid, elatgrid, elevations,
                    levels=contour_levels, transform=ccrs.PlateCarree(), **contour_kwargs, )

    if contour_labels:
        ax.text(-146, 70.775,'100 m',rotation=-12, transform=ccrs.PlateCarree(), **text_kwargs)
        ax.text(-146.5, 70.25,'20 m',rotation=-15, transform=ccrs.PlateCarree(), **text_kwargs)
