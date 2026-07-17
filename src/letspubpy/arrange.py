import numpy as np
from lets_plot import gggrid, theme
from .plots import wrap_plot

def ggarrange(*plots, ncol=None, nrow=None, widths=None, heights=None, common_legend=False, legend="bottom"):
    """
    Arrange multiple plots in a grid, mimicking ggpubr::ggarrange().
    
    Parameters
    ----------
    plots : PlotSpec or list/tuple of PlotSpec
        The plots to arrange. Can be passed as individual arguments or as a list/tuple.
    ncol : int, optional
        Number of columns in the grid.
    nrow : int, optional
        Number of rows in the grid.
    widths : list of float, optional
        Relative widths of columns.
    heights : list of float, optional
        Relative heights of rows.
    common_legend : bool, default=False
        If True, collect and combine legends into a single legend.
    legend : str, default="bottom"
        Position of the combined legend ("top", "bottom", "left", "right", "none").
    """
    if len(plots) == 1 and isinstance(plots[0], (list, tuple)):
        plot_list = list(plots[0])
    else:
        plot_list = list(plots)
        
    n = len(plot_list)
    if n == 0:
        raise ValueError("Must provide at least one plot to arrange.")
        
    # Infer ncol and nrow if not fully specified
    if ncol is None and nrow is None:
        ncol = n
    elif ncol is None:
        ncol = int(np.ceil(n / nrow))
        
    guides = 'collect' if common_legend else 'keep'
    
    grid = gggrid(plot_list, ncol=ncol, widths=widths, heights=heights, guides=guides, align=True)
    
    if common_legend:
        grid += theme(legend_position=legend)
        
    # Wrap the output so it supports further additions/customization
    return wrap_plot(grid)
