import numpy as np
import pandas as pd
from lets_plot import (
    ggplot as _ggplot,
    geom_boxplot,
    geom_violin,
    geom_jitter,
    geom_dotplot,
    geom_bar,
    geom_line,
    geom_point,
    geom_smooth,
    geom_histogram,
    geom_density,
    geom_pie,
    geom_errorbar,
    position_dodge,
    aes,
    ggtitle,
    xlab,
    ylab,
    scale_x_discrete,
    theme,
    layer_labels
)
from lets_plot.plot.core import PlotSpec

from .theme import theme_pubr, scale_color_pubr, scale_fill_pubr

class PubPlotSpec(PlotSpec):
    """Subclass of lets_plot.plot.core.PlotSpec that handles custom python addition via __radd__."""
    def __add__(self, other):
        if hasattr(other, '__radd__'):
            return other.__radd__(self)
        res = super().__add__(other)
        if isinstance(res, PlotSpec):
            res.__class__ = PubPlotSpec
        return res

def wrap_plot(plot):
    """Cast a standard PlotSpec into a PubPlotSpec."""
    if isinstance(plot, PlotSpec):
        plot.__class__ = PubPlotSpec
    return plot

def ggplot(*args, **kwargs):
    """Create a new lets-plot ggplot using PubPlotSpec."""
    p = _ggplot(*args, **kwargs)
    p.__class__ = PubPlotSpec
    return p

def get_color_fill_aes_and_params(data, color, fill):
    """Split color and fill arguments into aesthetic mappings or constant parameters."""
    mapping = {}
    params = {}
    
    if color is not None:
        if isinstance(color, str) and color in data.columns:
            mapping['color'] = color
        else:
            params['color'] = color
            
    if fill is not None:
        if isinstance(fill, str) and fill in data.columns:
            mapping['fill'] = fill
        else:
            params['fill'] = fill
            
    return mapping, params

def apply_labels_and_theme(p, title=None, xlab_str=None, ylab_str=None, order=None, show_legend=True, ggtheme=None):
    """Helper to apply standard titles, axis labels, category ordering, and themes."""
    if title:
        p += ggtitle(title)
    if xlab_str is not None:
        p += xlab(xlab_str)
    if ylab_str is not None:
        p += ylab(ylab_str)
        
    if order is not None:
        p += scale_x_discrete(limits=order)
        
    theme_obj = ggtheme if ggtheme is not None else theme_pubr()
    if not show_legend:
        theme_obj += theme(legend_position='none')
        
    p += theme_obj
    return p

def add_extra_layers(p, x, y, add, add_params, data, color, fill):
    """Helper to add secondary layers like jitter, points, or boxplots to the main plot."""
    if not add or add == "none":
        return p
        
    if isinstance(add, str):
        add = [add]
        
    for item in add:
        item_params = add_params.copy() if add_params else {}
        
        if item in ["jitter", "stripchart"]:
            l_mapping = aes(x=x, y=y)
            if color in data.columns:
                l_mapping = aes(x=x, y=y, color=color)
            else:
                if 'color' not in item_params:
                    item_params['color'] = color if color != 'white' else 'black'
            if 'width' not in item_params:
                item_params['width'] = 0.2
            if 'height' not in item_params:
                item_params['height'] = 0.0
            p += geom_jitter(l_mapping, **item_params)
            
        elif item == "boxplot":
            l_mapping = aes(x=x, y=y)
            if fill in data.columns:
                l_mapping = aes(x=x, y=y, fill=fill)
            else:
                if 'fill' not in item_params:
                    item_params['fill'] = 'white'
            if 'color' not in item_params:
                item_params['color'] = 'black'
            if 'width' not in item_params:
                item_params['width'] = 0.15
            if 'outlier_shape' not in item_params:
                item_params['outlier_shape'] = 'blank'
            p += geom_boxplot(l_mapping, **item_params)
            
        elif item == "violin":
            l_mapping = aes(x=x, y=y)
            if fill in data.columns:
                l_mapping = aes(x=x, y=y, fill=fill)
            else:
                if 'fill' not in item_params:
                    item_params['fill'] = 'white'
            p += geom_violin(l_mapping, **item_params)
            
        elif item == "dotplot":
            l_mapping = aes(x=x, y=y)
            if fill in data.columns:
                l_mapping = aes(x=x, y=y, fill=fill)
            p += geom_dotplot(l_mapping, binaxis='y', stackdir='center', **item_params)
            
        elif item == "point":
            l_mapping = aes(x=x, y=y)
            if color in data.columns:
                l_mapping = aes(x=x, y=y, color=color)
            else:
                if 'color' not in item_params:
                    item_params['color'] = color if color != 'white' else 'black'
            p += geom_point(l_mapping, **item_params)
            
    return p

def ggboxplot(data, x, y, color="black", fill="white", palette="npg", width=0.7, size=None, notch=False,
              outlier_shape=19, outlier_color=None, outlier_size=None, add="none", add_params=None,
              order=None, select=None, remove=None, title=None, xlab=None, ylab=None, show_legend=True, ggtheme=None):
    """Create a publication-ready boxplot."""
    df = data.copy()
    if select is not None:
        df = df[df[x].isin(select)]
    if remove is not None:
        df = df[~df[x].isin(remove)]
        
    mapping = aes(x=x, y=y)
    geom_mapping, geom_params = get_color_fill_aes_and_params(df, color, fill)
    
    p = ggplot(df, mapping)
    
    bp_params = {
        'width': width,
        'notch': notch,
    }
    if size is not None:
        bp_params['size'] = size
    if outlier_shape is not None:
        bp_params['outlier_shape'] = outlier_shape
    if outlier_color is not None:
        bp_params['outlier_color'] = outlier_color
    if outlier_size is not None:
        bp_params['outlier_size'] = outlier_size
        
    bp_params.update(geom_params)
    
    p += geom_boxplot(aes(**geom_mapping), **bp_params)
    
    if 'color' in geom_mapping:
        p += scale_color_pubr(palette)
    if 'fill' in geom_mapping:
        p += scale_fill_pubr(palette)
        
    if add != "none":
        p = add_extra_layers(p, x, y, add, add_params, df, color, fill)
        
    p = apply_labels_and_theme(p, title, xlab, ylab, order, show_legend, ggtheme)
    return p

def ggviolin(data, x, y, color="black", fill="white", palette="npg", width=1.0, size=None, draw_quantiles=None,
             add="none", add_params=None, order=None, select=None, remove=None, title=None, xlab=None, ylab=None,
             show_legend=True, ggtheme=None):
    """Create a publication-ready violin plot."""
    df = data.copy()
    if select is not None:
        df = df[df[x].isin(select)]
    if remove is not None:
        df = df[~df[x].isin(remove)]
        
    mapping = aes(x=x, y=y)
    geom_mapping, geom_params = get_color_fill_aes_and_params(df, color, fill)
    
    p = ggplot(df, mapping)
    
    v_params = {'width': width}
    if size is not None:
        v_params['size'] = size
    if draw_quantiles is not None:
        v_params['draw_quantiles'] = draw_quantiles
        
    v_params.update(geom_params)
    
    p += geom_violin(aes(**geom_mapping), **v_params)
    
    if 'color' in geom_mapping:
        p += scale_color_pubr(palette)
    if 'fill' in geom_mapping:
        p += scale_fill_pubr(palette)
        
    if add != "none":
        p = add_extra_layers(p, x, y, add, add_params, df, color, fill)
        
    p = apply_labels_and_theme(p, title, xlab, ylab, order, show_legend, ggtheme)
    return p

def ggdotplot(data, x, y, color="black", fill="white", palette="npg", binwidth=None, size=None,
              add="none", add_params=None, order=None, select=None, remove=None, title=None, xlab=None, ylab=None,
              show_legend=True, ggtheme=None):
    """Create a publication-ready dotplot."""
    df = data.copy()
    if select is not None:
        df = df[df[x].isin(select)]
    if remove is not None:
        df = df[~df[x].isin(remove)]
        
    mapping = aes(x=x, y=y)
    geom_mapping, geom_params = get_color_fill_aes_and_params(df, color, fill)
    
    p = ggplot(df, mapping)
    
    dp_params = {'binaxis': 'y', 'stackdir': 'center'}
    if binwidth is not None:
        dp_params['binwidth'] = binwidth
    if size is not None:
        dp_params['dotsize'] = size
        
    dp_params.update(geom_params)
    
    p += geom_dotplot(aes(**geom_mapping), **dp_params)
    
    if 'color' in geom_mapping:
        p += scale_color_pubr(palette)
    if 'fill' in geom_mapping:
        p += scale_fill_pubr(palette)
        
    if add != "none":
        p = add_extra_layers(p, x, y, add, add_params, df, color, fill)
        
    p = apply_labels_and_theme(p, title, xlab, ylab, order, show_legend, ggtheme)
    return p

def ggstripchart(data, x, y, color="black", fill="white", palette="npg", shape=19, size=None, jitter=0.2,
                 add="none", add_params=None, order=None, select=None, remove=None, title=None, xlab=None, ylab=None,
                 show_legend=True, ggtheme=None):
    """Create a publication-ready stripchart (jitter plot)."""
    df = data.copy()
    if select is not None:
        df = df[df[x].isin(select)]
    if remove is not None:
        df = df[~df[x].isin(remove)]
        
    mapping = aes(x=x, y=y)
    geom_mapping, geom_params = get_color_fill_aes_and_params(df, color, fill)
    
    p = ggplot(df, mapping)
    
    sc_params = {}
    if jitter is not None:
        sc_params['width'] = jitter
        sc_params['height'] = 0.0
    if size is not None:
        sc_params['size'] = size
    if shape is not None:
        if isinstance(shape, str) and shape in df.columns:
            geom_mapping['shape'] = shape
        else:
            sc_params['shape'] = shape
            
    sc_params.update(geom_params)
    
    p += geom_jitter(aes(**geom_mapping), **sc_params)
    
    if 'color' in geom_mapping:
        p += scale_color_pubr(palette)
    if 'fill' in geom_mapping:
        p += scale_fill_pubr(palette)
        
    if add != "none":
        p = add_extra_layers(p, x, y, add, add_params, df, color, fill)
        
    p = apply_labels_and_theme(p, title, xlab, ylab, order, show_legend, ggtheme)
    return p

def ggbarplot(data, x, y=None, color="black", fill="white", palette="npg", width=0.7, size=None,
              add="none", add_params=None, order=None, select=None, remove=None,
              title=None, xlab=None, ylab=None, show_legend=True, ggtheme=None, position=None):
    """Create a publication-ready barplot. Statically aggregates means/error bars if y is numeric with multiple observations."""
    df = data.copy()
    if select is not None:
        df = df[df[x].isin(select)]
    if remove is not None:
        df = df[~df[x].isin(remove)]
        
    group_col = None
    if fill in df.columns:
        group_col = fill
    elif color in df.columns:
        group_col = color
        
    if position is None:
        position = position_dodge(0.8) if group_col else 'identity'
        
    geom_mapping, geom_params = get_color_fill_aes_and_params(df, color, fill)
    
    if y is None:
        # Plot counts
        mapping = aes(x=x)
        p = ggplot(df, mapping)
        p += geom_bar(aes(**geom_mapping), width=width, **geom_params)
    else:
        # Plot mean/identity
        groupby_cols = [x]
        if group_col:
            groupby_cols.append(group_col)
            
        # Group and aggregate
        agg_df = df.groupby(groupby_cols, as_index=False).agg(
            mean_y=(y, 'mean'),
            sd_y=(y, 'std'),
            count_y=(y, 'count')
        )
        agg_df['se_y'] = agg_df['sd_y'] / np.sqrt(agg_df['count_y'])
        agg_df['se_y'] = agg_df['se_y'].fillna(0)
        agg_df['sd_y'] = agg_df['sd_y'].fillna(0)
        
        agg_mapping = aes(x=x, y='mean_y')
        p = ggplot(agg_df, agg_mapping)
        
        bp_params = {'stat': 'identity', 'width': width, 'position': position}
        if size is not None:
            bp_params['size'] = size
        bp_params.update(geom_params)
        
        p += geom_bar(aes(**geom_mapping), **bp_params)
        
        if add != "none":
            if isinstance(add, str):
                add = [add]
            for item in add:
                item_params = add_params.copy() if add_params else {}
                if item == "mean_se":
                    agg_df['ymin'] = agg_df['mean_y'] - agg_df['se_y']
                    agg_df['ymax'] = agg_df['mean_y'] + agg_df['se_y']
                    eb_mapping = aes(ymin='ymin', ymax='ymax')
                    if group_col:
                        eb_mapping = aes(ymin='ymin', ymax='ymax', group=group_col)
                    if 'width' not in item_params:
                        item_params['width'] = 0.2
                    p += geom_errorbar(eb_mapping, position=position, **item_params)
                elif item == "mean_sd":
                    agg_df['ymin'] = agg_df['mean_y'] - agg_df['sd_y']
                    agg_df['ymax'] = agg_df['mean_y'] + agg_df['sd_y']
                    eb_mapping = aes(ymin='ymin', ymax='ymax')
                    if group_col:
                        eb_mapping = aes(ymin='ymin', ymax='ymax', group=group_col)
                    if 'width' not in item_params:
                        item_params['width'] = 0.2
                    p += geom_errorbar(eb_mapping, position=position, **item_params)
                    
    if 'color' in geom_mapping:
        p += scale_color_pubr(palette)
    if 'fill' in geom_mapping:
        p += scale_fill_pubr(palette)
        
    p = apply_labels_and_theme(p, title, xlab, ylab, order, show_legend, ggtheme)
    return p

def ggline(data, x, y, color="black", fill="white", palette="npg", size=None,
           add="none", add_params=None, order=None, select=None, remove=None,
           title=None, xlab=None, ylab=None, show_legend=True, ggtheme=None, position=None):
    """Create a publication-ready line plot of group means."""
    df = data.copy()
    if select is not None:
        df = df[df[x].isin(select)]
    if remove is not None:
        df = df[~df[x].isin(remove)]
        
    group_col = None
    if color in df.columns:
        group_col = color
    elif fill in df.columns:
        group_col = fill
        
    if position is None:
        position = position_dodge(0.2) if group_col else 'identity'
        
    geom_mapping, geom_params = get_color_fill_aes_and_params(df, color, fill)
    
    groupby_cols = [x]
    if group_col:
        groupby_cols.append(group_col)
        
    agg_df = df.groupby(groupby_cols, as_index=False).agg(
        mean_y=(y, 'mean'),
        sd_y=(y, 'std'),
        count_y=(y, 'count')
    )
    agg_df['se_y'] = agg_df['sd_y'] / np.sqrt(agg_df['count_y'])
    agg_df['se_y'] = agg_df['se_y'].fillna(0)
    agg_df['sd_y'] = agg_df['sd_y'].fillna(0)
    
    line_mapping = aes(x=x, y='mean_y')
    if group_col:
        line_mapping = aes(x=x, y='mean_y', group=group_col)
    else:
        line_mapping = aes(x=x, y='mean_y', group=1)
        
    p = ggplot(agg_df, line_mapping)
    
    line_params = geom_params.copy()
    if size is not None:
        line_params['size'] = size
    p += geom_line(aes(**geom_mapping), position=position, **line_params)
    
    point_params = geom_params.copy()
    if size is not None:
        point_params['size'] = size * 2
    else:
        point_params['size'] = 3
    p += geom_point(aes(**geom_mapping), position=position, **point_params)
    
    if add != "none":
        if isinstance(add, str):
            add = [add]
        for item in add:
            item_params = add_params.copy() if add_params else {}
            if item == "mean_se":
                agg_df['ymin'] = agg_df['mean_y'] - agg_df['se_y']
                agg_df['ymax'] = agg_df['mean_y'] + agg_df['se_y']
                eb_mapping = aes(ymin='ymin', ymax='ymax')
                if group_col:
                    eb_mapping = aes(ymin='ymin', ymax='ymax', group=group_col)
                if 'width' not in item_params:
                    item_params['width'] = 0.1
                p += geom_errorbar(eb_mapping, position=position, **item_params)
            elif item == "mean_sd":
                agg_df['ymin'] = agg_df['mean_y'] - agg_df['sd_y']
                agg_df['ymax'] = agg_df['mean_y'] + agg_df['sd_y']
                eb_mapping = aes(ymin='ymin', ymax='ymax')
                if group_col:
                    eb_mapping = aes(ymin='ymin', ymax='ymax', group=group_col)
                if 'width' not in item_params:
                    item_params['width'] = 0.1
                p += geom_errorbar(eb_mapping, position=position, **item_params)
                
    if 'color' in geom_mapping:
        p += scale_color_pubr(palette)
    if 'fill' in geom_mapping:
        p += scale_fill_pubr(palette)
        
    p = apply_labels_and_theme(p, title, xlab, ylab, order, show_legend, ggtheme)
    return p

def ggscatter(data, x, y, color="black", fill=None, palette="npg", shape=19, size=None,
              add="none", add_params=None, title=None, xlab=None, ylab=None,
              show_legend=True, ggtheme=None):
    """Create a publication-ready scatter plot with optional regression lines."""
    df = data.copy()
    mapping = aes(x=x, y=y)
    geom_mapping, geom_params = get_color_fill_aes_and_params(df, color, fill)
    
    p = ggplot(df, mapping)
    
    pt_params = {}
    if size is not None:
        pt_params['size'] = size
    if shape is not None:
        if isinstance(shape, str) and shape in df.columns:
            geom_mapping['shape'] = shape
        else:
            pt_params['shape'] = shape
            
    pt_params.update(geom_params)
    p += geom_point(aes(**geom_mapping), **pt_params)
    
    if 'color' in geom_mapping:
        p += scale_color_pubr(palette)
    if 'fill' in geom_mapping:
        p += scale_fill_pubr(palette)
        
    if add != "none":
        if isinstance(add, str):
            add = [add]
        for item in add:
            item_params = add_params.copy() if add_params else {}
            if item == "reg.line":
                if 'method' not in item_params:
                    item_params['method'] = 'lm'
                if 'se' not in item_params:
                    item_params['se'] = True
                p += geom_smooth(aes(**geom_mapping), **item_params)
            else:
                p = add_extra_layers(p, x, y, [item], add_params, df, color, fill)
                
    p = apply_labels_and_theme(p, title, xlab, ylab, None, show_legend, ggtheme)
    return p

def gghistogram(data, x, y="..count..", color="black", fill="white", palette="npg",
                bins=30, size=None, title=None, xlab=None, ylab=None, show_legend=True, ggtheme=None):
    """Create a publication-ready histogram."""
    df = data.copy()
    mapping = aes(x=x)
    geom_mapping, geom_params = get_color_fill_aes_and_params(df, color, fill)
    
    p = ggplot(df, mapping)
    
    h_params = {'bins': bins}
    if size is not None:
        h_params['size'] = size
    h_params.update(geom_params)
    
    if y is not None:
        geom_mapping['y'] = y
        
    p += geom_histogram(aes(**geom_mapping), **h_params)
    
    if 'color' in geom_mapping:
        p += scale_color_pubr(palette)
    if 'fill' in geom_mapping:
        p += scale_fill_pubr(palette)
        
    p = apply_labels_and_theme(p, title, xlab, ylab, None, show_legend, ggtheme)
    return p

def ggdensity(data, x, y="..density..", color="black", fill="white", palette="npg",
              size=None, title=None, xlab=None, ylab=None, show_legend=True, ggtheme=None):
    """Create a publication-ready density plot."""
    df = data.copy()
    mapping = aes(x=x)
    geom_mapping, geom_params = get_color_fill_aes_and_params(df, color, fill)
    
    p = ggplot(df, mapping)
    
    d_params = {}
    if size is not None:
        d_params['size'] = size
    d_params.update(geom_params)
    
    if y is not None:
        geom_mapping['y'] = y
        
    p += geom_density(aes(**geom_mapping), **d_params)
    
    if 'color' in geom_mapping:
        p += scale_color_pubr(palette)
    if 'fill' in geom_mapping:
        p += scale_fill_pubr(palette)
        
    p = apply_labels_and_theme(p, title, xlab, ylab, None, show_legend, ggtheme)
    return p

def ggpie(data, x, label, fill=None, palette="npg", size=None, hole=0.0, title=None, show_legend=True, ggtheme=None):
    """Create a publication-ready pie chart."""
    from lets_plot import theme_void
    df = data.copy()
    fill_col = fill if fill is not None else label
    
    mapping = aes(slice=x, fill=fill_col)
    geom_mapping, geom_params = get_color_fill_aes_and_params(df, None, fill_col)
    
    p = ggplot(df)
    
    pie_params = {
        'stat': 'identity',
        'hole': hole,
        'labels': layer_labels([label])
    }
    if size is not None:
        pie_params['size'] = size
    pie_params.update(geom_params)
    
    p += geom_pie(mapping, **pie_params)
    
    if fill_col in df.columns:
        p += scale_fill_pubr(palette)
        
    theme_obj = ggtheme if ggtheme is not None else theme_void()
    if not show_legend:
        theme_obj += theme(legend_position='none')
        
    p += theme_obj
    if title:
        p += ggtitle(title)
        
    return p

def ggdonutchart(data, x, label, fill=None, palette="npg", size=None, hole=0.4, title=None, show_legend=True, ggtheme=None):
    """Create a publication-ready donut chart."""
    return ggpie(data, x, label, fill=fill, palette=palette, size=size, hole=hole, title=title, show_legend=show_legend, ggtheme=ggtheme)
