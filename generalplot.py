# Functions for plotting

# DEPENDENCIES:
import matplotlib.colors
import numpy as np, numpy.ma as ma
import matplotlib.cm as cm
# import cartopy, cartopy.crs as ccrs

# FUNCTIONS:
#---------------------------------------------------------------------
class TwopointNormalize(matplotlib.colors.Normalize):
    
    """Class for normalizing colormap based off two midpoints.

INPUT: 
- vmin: min value
- vmid1: lower midpoint value
- vmid2: higher midpoint value
- vmax: max value

OUTPUT:
- normalization scaling [vmin, vmid1, vmid2, vmax] to [0, 1/3, 2/3, 1] of colormap

Latest recorded update:
12-17-2024
    """
        
    def __init__(self, vmin=None, vmax=None, vmid1=None, vmid2=None, clip=False):
        self.vmid1 = vmid1
        self.vmid2 = vmid2
        super().__init__(vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.vmid1, self.vmid2, self.vmax], [0, 0.33,0.66, 1]
        return np.ma.masked_array(np.interp(value, x, y))
    




def add_colorbar(fig, ax, colorbar_input, cb_placement = 'left', cb_orientation = 'auto', 
                 cb_width = 'auto',  cb_length_fraction = [0,1], cb_pad = 0, 
                 cb_ticks = 'auto', cb_ticklabels = 'auto', 
                 cb_extend='neither', cb_label=' ', labelpad = 'auto', 
                 cb_label_placement = 'auto', cb_tick_placement = 'auto',
                 tick_kwargs = None,
                 cb_labelsize = 12, draw_edges=False, edge_params=['k',2]):

    """Function for plotting colorbar along edge of figure axis.

INPUT: 
- fig: figure to which colorbar will be added
- ax: figure axis to which colorbar will be added
- colorbar_input: either specify [matplotlib.collections.QuadMesh], pmatplotlib.cm.ScalarMappable] (from pcolormesh plot output),
                    [cartopy.mpl.contour.GeoContourSet] (from countourf output),
                  or specify [cmap, norm] 
                   where cmap is matplotlib cmap (e.g. 'RdBu')
                   where norm is matplotlib.colors normlalization instance (e.g. made from TwoSlopeNorm)
- cb_placement: location of colorbar, as 'left' (default),'right','top','bottom'
- cb_orientation: orientation ('horizontal' or 'vertical') of colorbar. Set to 'auto' (default) to 
                  pick automatically based off its cb_placement
- cb_label_placement: location of colorbar label:
        for cb_orientation = 'horizontal': can either be 'auto' (outwards from plot), 'left', or 'right'
        for cb_orientation = 'vertical': can either be 'auto' (outwards from plot), 'top', or 'bottom'
    
- cb_tick_placement: location of colorbar ticks:
        for cb_orientation = 'horizontal': can either be 'auto' (outwards from plot), 'left', or 'right'
        for cb_orientation = 'vertical': can either be 'auto' (outwards from plot), 'top', or 'bottom'
- cb_width: colorbar width (default: 'auto', which makes it 1/20 figure width)
- cb_length_fraction: beginning and end position of colorbar along axis as [begin, end], as fraction of axis length 
                      (default: [0,1] for cbar to stretch along full axis)
- cb_pad: pad between plot and colorbar (default: 0)
- cb_ticks: colorbar ticks. 'auto' (default) selects automatically from data, or provide ticks as list (e.g. [1,2,3])
- cb_ticklabels:  colorbar tick labels
             'auto' (default) selects automatically from data, or provide ticks as list (e.g. ['<1','2','>3'])
              if providing list, must match number of provided cb_ticks
- cb_extend: end cap style for colorbar (to address out-of-range values), either:
           --> 'neither': (default) flat ends at either end
           --> 'min': arrow at min end of colorbar
           --> 'max': arrow at max end of colorbar
           --> 'both': arrow at both ends of colorbar
- cb_label: colorbar label (string), default is empty string
- labelpad: pad between colorbar and label, either 'auto' to use default setting or specify float
- tick_kwargs: kwargs for tick parameters (default None)
    e.g. tick_kwargs = {'pad':0.1, 'length':0, 'labelsize':40, 'length':0.1, 'width':4}
- cb_labelsize: colorbar label and tick fontsize
- draw_edges: bool, whether or not to draw outline around colorbar (default: False)
- edge_params: color and linewidth for cbar edges if drawn, as [edgecolor, edgelinewidth] (default: ['k',2])


OUTPUT:
- cbar: colorbar instance
- cbar_ax: colorbar axis instance

Latest recorded update:
12-17-2024
    """
    
    
    # determine type of colorbar input 
    #=================================
    # if colorbar_input is [QuadMesh] from plot output
    if len(colorbar_input) == 1:
        if isinstance(colorbar_input[0], matplotlib.collections.QuadMesh) or isinstance(colorbar_input[0], cartopy.mpl.contour.GeoContourSet) or isinstance(colorbar_input[0], matplotlib.cm.ScalarMappable):
            
            CB_INPUT = colorbar_input[0]
        else:
            print('colorbar_input is not type matplotlib.collections.QuadMesh nor cartopy.mpl.contour.GeoContourSet')
    # if colorbar_input is [cmap, norm]
    elif len(colorbar_input) == 2:
        CB_INPUT = cm.ScalarMappable(norm=colorbar_input[1], cmap=colorbar_input[0])
    else:
        print('unrecognized colorbar_input, should be of length 1 or 2')
    
    # generate plot axes
    #=================================
    # get plot axes corner coordinates
    plot_axis_coords = ax.get_position().get_points()
    ax_x0 = plot_axis_coords[0][0]
    ax_x1 = plot_axis_coords[1][0]
    ax_y0 = plot_axis_coords[0][1]
    ax_y1 = plot_axis_coords[1][1]
    
    # grab desored fractional lengths of colorbar
    #============================================
    cb_L_i = cb_length_fraction[0]
    cb_L_f = cb_length_fraction[1] 

    # set widths of colorbar based of specification or 1/10 figure width
    if str(cb_width) == 'auto':
        if str(cb_placement) == 'top' or str(cb_placement) == 'bottom':
            WIDTH = 0.05*(ax_y1-ax_y0)
        else:
            WIDTH = 0.05*(ax_x1-ax_x0)
    else:
        WIDTH = cb_width

    # generate colorbar axis based off desired edge of placement
    if str(cb_placement) == 'left':  
        cbar_ax = fig.add_axes([ax_x0-(WIDTH+cb_pad), ax_y0+(cb_L_i*(ax_y1-ax_y0)), WIDTH, (ax_y1-ax_y0)*(cb_L_f-cb_L_i)])
    elif str(cb_placement) == 'right':
        cbar_ax = fig.add_axes([ax_x1+cb_pad, ax_y0+(cb_L_i*(ax_y1-ax_y0)), WIDTH, (ax_y1-ax_y0)*(cb_L_f-cb_L_i)])
    elif str(cb_placement) == 'top':
        cbar_ax = fig.add_axes([ax_x0+(cb_L_i*(ax_x1-ax_x0)), ax_y1+cb_pad, (ax_x1-ax_x0)*(cb_L_f-cb_L_i), WIDTH])
    else:
        cbar_ax = fig.add_axes([ax_x0+(cb_L_i*(ax_x1-ax_x0)), ax_y0-(WIDTH+cb_pad), (ax_x1-ax_x0)*(cb_L_f-cb_L_i), WIDTH])
        
    # set colorbar orientation from its placement
    if str(cb_orientation) == 'auto':
        if str(cb_placement) == 'top' or str(cb_placement) == 'bottom':
            cb_orientation = 'horizontal'
        else:
            cb_orientation = 'vertical'

    # make colorbar and place labels
    #====================================
    # if colorbar ticks not provided, automatically place ticks
    if str(cb_ticks) == 'auto':
        cbar = fig.colorbar(CB_INPUT,cax=cbar_ax, 
                            orientation=cb_orientation, extend=cb_extend, drawedges=draw_edges)

    # if colorbar ticks provided, place as specified
    else:
        cbar = fig.colorbar(CB_INPUT,cax=cbar_ax, 
                            orientation=cb_orientation, extend=cb_extend, ticks=cb_ticks, drawedges=draw_edges)
        # place tick labels if specified
        if str(cb_ticklabels)!='auto':
            if str(cb_orientation) == 'horizontal':
                cbar.ax.set_xticklabels(cb_ticklabels) 
            else:
                cbar.ax.set_yticklabels(cb_ticklabels) 
    
    
    # tick parameters from tick_kwargs
    if tick_kwargs != None:
        if str(cb_orientation) == 'horizontal':
            cbar.ax.xaxis.set_tick_params(**tick_kwargs)
        else:
            cbar.ax.yaxis.set_tick_params(**tick_kwargs)
            

    # if including edge border around cbar, specify its linewidth and color            
    if draw_edges==True:
        cbar.outline.set_color(edge_params[0])
        cbar.outline.set_linewidth(edge_params[1])
    
    # remove gray facecolor behind colorbar arrow cap if extending at either end
    if str(cb_extend) != 'neither':
        cbar.ax.set_facecolor('none')
        
    # set label and colorbar fontsize
    cbar.ax.tick_params(labelsize=cb_labelsize)
    if str(labelpad) == 'auto':
        cbar.set_label(cb_label, fontsize=cb_labelsize, rotation=0)
    else:
        cbar.set_label(cb_label, fontsize=cb_labelsize, rotation=0, labelpad=labelpad)
    
    # choose side of colorbar to place label
    if str(cb_label_placement) == 'auto':
        # place label on outer side of plot for various colorbar positions
        if str(cb_placement) == 'top' or str(cb_placement) == 'bottom':
            cbar_ax.xaxis.set_label_position(cb_placement)
        else:
            cbar_ax.yaxis.set_label_position(cb_placement)
    
    # place label on specified side of colorbar
    else:
        if str(cb_orientation) == 'horizontal':
            cbar_ax.xaxis.set_label_position(cb_label_placement) # 'top' or 'bottom'
        else:
            cbar_ax.yaxis.set_label_position(cb_label_placement) # 'left' or 'right'
            
    # choose side of colorbar to place ticks
    if str(cb_tick_placement) == 'auto':
        # place ticks on outer side of plot for various colorbar positions
        if str(cb_placement) == 'top' or str(cb_placement) == 'bottom':
            cbar_ax.xaxis.set_ticks_position(cb_placement)
        else:
            cbar_ax.yaxis.set_ticks_position(cb_placement)
    # place ticks on specified side of colorbar
    else:
        if str(cb_orientation) == 'horizontal':
            cbar_ax.xaxis.set_ticks_position(cb_tick_placement) # 'top' or 'bottom'
        else:
            cbar_ax.yaxis.set_ticks_position(cb_tick_placement) # 'left' or 'right'

    return cbar, cbar_ax

