import numpy as np
import pandas as pd
from scipy import stats as _scipy_stats
from scipy.spatial import ConvexHull as _ConvexHull
from scipy.spatial.distance import pdist as _pdist, squareform as _squareform
from scipy.cluster.hierarchy import linkage as _linkage, dendrogram as _dendrogram, fcluster as _fcluster
from scipy.ndimage import gaussian_filter1d as _gaussian_filter1d
from scipy.optimize import curve_fit as _curve_fit
from scipy.stats import gaussian_kde as _gaussian_kde, chi2 as _chi2
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
    geom_polygon,
    geom_text,
    geom_blank,
    geom_tile,
    geom_rect,
    geom_segment,
    geom_ribbon,
    geom_qq,
    geom_qq2,
    geom_qq_line,
    geom_qq2_line,
    stat_ecdf,
    coord_fixed,
    position_dodge,
    aes,
    ggtitle,
    xlab as _xlab,
    ylab as _ylab,
    scale_x_discrete,
    scale_y_discrete,
    scale_y_continuous,
    scale_x_continuous,
    scale_fill_gradient2,
    facet_grid,
    theme,
    theme_bw,
    theme_void,
    element_blank,
    element_rect,
    layer_labels,
    gggrid,
    ggsize,
    scale_fill_identity,
    scale_color_identity,
    scale_color_manual,
    scale_fill_manual,
    scale_color_gradient,
    scale_size,
    guides,
    layer_tooltips,
    geom_hline,
    geom_vline
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
        p += _xlab(xlab_str)
    if ylab_str is not None:
        p += _ylab(ylab_str)
        
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
        if group_col and group_col != x:
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


def confidence_ellipse_points(mean, cov, n_points=120, level=0.95, ellipse_type="norm", n=None):
    """Return the coordinates of a 2D confidence ellipse boundary.

    Parameters
    ----------
    mean : array-like of shape (2,)
        Center of the ellipse.
    cov : array-like of shape (2, 2)
        Covariance matrix.
    n_points : int
        Number of boundary points.
    level : float
        Confidence level, e.g. 0.95 for a 95% ellipse.
    ellipse_type : str
        One of ``"norm"``, ``"t"``, or ``"euclid"``.
        * ``"norm"``: Multivariate normal (chi-square, df=2).
        * ``"t"``: Hotelling T-squared, using the F-distribution for 2D.
        * ``"euclid"``: Equal-radius circle (useful when covariates are
          standardized / on the same scale).
    n : int or None
        Sample size, required when ``ellipse_type="t"``.
    """
    mean = np.asarray(mean, dtype=float)
    cov = np.asarray(cov, dtype=float)
    if mean.shape != (2,):
        raise ValueError("mean must have shape (2,)")
    if cov.shape != (2, 2):
        raise ValueError("cov must have shape (2, 2)")

    if ellipse_type == "norm":
        scale = _scipy_stats.chi2.ppf(level, df=2)
    elif ellipse_type == "t":
        if n is None or n < 3:
            raise ValueError("n (sample size) must be provided and >= 3 for ellipse_type='t'")
        F = _scipy_stats.f.ppf(level, dfn=2, dfd=n - 2)
        scale = 2 * F * (n - 1) / (n - 2)
    elif ellipse_type == "euclid":
        # Equal-radius circle: use a spherical covariance (identity) and scale
        # by the average variance
        avg_var = (cov[0, 0] + cov[1, 1]) / 2
        r = np.sqrt(avg_var * _scipy_stats.chi2.ppf(level, df=2))
        theta = np.linspace(0, 2 * np.pi, n_points)
        circle = np.column_stack([r * np.cos(theta), r * np.sin(theta)])
        return circle + mean
    else:
        raise ValueError(f"Unknown ellipse_type: {ellipse_type}")

    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals = vals[order]
    vecs = vecs[:, order]
    vals = np.clip(vals, a_min=1e-12, a_max=None)

    widths = np.sqrt(vals * scale)
    theta = np.linspace(0, 2 * np.pi, n_points)
    circle = np.vstack([np.cos(theta), np.sin(theta)])
    ellipse = np.diag(widths) @ circle
    ellipse = vecs @ ellipse
    ellipse = ellipse + mean[:, None]
    return ellipse.T


def build_ellipse_df(df, x_col, y_col, group_col=None, level=0.95,
                     ellipse_type="norm", n_points=120):
    """Build a long-form DataFrame of ellipse boundary points.

    Parameters
    ----------
    df : pd.DataFrame
        Source data.
    x_col, y_col : str
        Column names for x and y.
    group_col : str or None
        Column name for grouping; if provided, one ellipse per group.
    level : float
        Confidence level.
    ellipse_type : str
        ``"norm"``, ``"t"``, or ``"euclid"``.
    n_points : int
        Number of boundary points per ellipse.

    Returns
    -------
    pd.DataFrame
        Long-form DataFrame with columns matching the input names and an
        optional grouping column, with a ``.group_index`` to help draw each
        ellipse as a single closed polygon.
    """
    rows = []
    if group_col is None:
        pts = df[[x_col, y_col]].dropna().values
        if len(pts) < 2:
            return pd.DataFrame(columns=[x_col, y_col, "_ellipse_group"])
        mean = pts.mean(axis=0)
        cov = np.cov(pts.T)
        n = len(pts)
        ell = confidence_ellipse_points(mean, cov, n_points=n_points,
                                        level=level, ellipse_type=ellipse_type, n=n)
        for i, (px, py) in enumerate(ell):
            rows.append({x_col: px, y_col: py, "_ellipse_group": 0})
        # Close the polygon
        rows.append({x_col: ell[0, 0], y_col: ell[0, 1], "_ellipse_group": 0})
    else:
        for gi, (g, sub) in enumerate(df.groupby(group_col, sort=False)):
            pts = sub[[x_col, y_col]].dropna().values
            if len(pts) < 2:
                continue
            mean = pts.mean(axis=0)
            cov = np.cov(pts.T)
            n = len(pts)
            ell = confidence_ellipse_points(mean, cov, n_points=n_points,
                                            level=level, ellipse_type=ellipse_type, n=n)
            for px, py in ell:
                rows.append({x_col: px, y_col: py, group_col: g, "_ellipse_group": gi})
            # Close the polygon by repeating the first point
            rows.append({x_col: ell[0, 0], y_col: ell[0, 1], group_col: g, "_ellipse_group": gi})
    return pd.DataFrame(rows)


def compute_correlation(x, y, method="pearson"):
    """Compute correlation coefficient and p-value.

    Parameters
    ----------
    x, y : array-like
        Numeric vectors of the same length.
    method : str
        ``"pearson"``, ``"spearman"``, or ``"kendall"``.

    Returns
    -------
    dict
        Dictionary with keys ``r``, ``p``, ``r2``, ``method_name``.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[mask], y[mask]
    if len(x) < 3:
        return {"r": np.nan, "p": np.nan, "r2": np.nan, "method_name": method}

    method_lower = method.lower()
    if method_lower == "pearson":
        r, p = _scipy_stats.pearsonr(x, y)
        method_name = "Pearson"
    elif method_lower == "spearman":
        r, p = _scipy_stats.spearmanr(x, y)
        method_name = "Spearman"
    elif method_lower == "kendall":
        tau, p = _scipy_stats.kendalltau(x, y)
        r = tau
        method_name = "Kendall"
    else:
        raise ValueError(f"Unknown correlation method: {method}")
    return {"r": r, "p": p, "r2": r ** 2, "method_name": method_name}


def ggscatter(data, x, y, color="black", fill=None, palette="npg", shape=19, size=None,
              add="none", add_params=None,
              ellipse=False, ellipse_level=0.95, ellipse_type="norm", ellipse_alpha=0.15,
              rug=False, rug_size=0.5,
              cor=False, cor_method="pearson", cor_coef=False, cor_size=12,
              label=None, label_size=4,
              confint=True, confint_level=0.95,
              aspect_ratio=None,
              position=None,
              title=None, xlab=None, ylab=None,
              show_legend=True, ggtheme=None):
    """Create a publication-ready scatter plot with optional overlay layers.

    Parameters
    ----------
    data : pd.DataFrame
        Input data.
    x, y : str
        Column names for x and y axes.
    color : str
        Column name or constant color for point outlines.
    fill : str
        Column name or constant color for point fills.
    palette : str
        Color palette name (e.g. ``"npg"``, ``"aaas"``).
    shape : int or str
        Point shape constant or column name mapping to shapes.
    size : float
        Point size.
    add : str or list of str
        Additional layers: ``"reg.line"``, ``"mean_se"``, ``"mean_sd"``,
        ``"jitter"``, ``"point"``.
    add_params : dict
        Extra parameters for the ``add`` layer.
    ellipse : bool
        If True, draws a confidence ellipse around each group (or overall).
    ellipse_level : float
        Confidence level for the ellipse, default 0.95.
    ellipse_type : str
        ``"norm"`` (chi-square), ``"t"`` (Hotelling T2), or ``"euclid"``.
    ellipse_alpha : float
        Transparency of the ellipse fill, default 0.15.
    rug : bool
        If True, adds marginal rug plots on both axes.
    rug_size : float
        Size of rug marks.
    cor : bool
        If True, shows the correlation coefficient on the plot.
    cor_method : str
        ``"pearson"``, ``"spearman"``, or ``"kendall"``.
    cor_coef : bool
        If True, shows R and R^2; if False, shows R and p-value.
    cor_size : int
        Font size of the correlation text.
    label : str
        Column name whose values will be used as point labels.
    label_size : float
        Font size for point labels.
    confint : bool
        If True (and ``add="reg.line"``), draws the confidence band.
    confint_level : float
        Confidence level for the regression band.
    aspect_ratio : float
        If set, enforces a fixed aspect ratio on the plot.
    position : object
        Position adjustment (e.g. ``position_dodge()``).
    title, xlab, ylab : str
        Labels.
    show_legend : bool
        Whether to show the legend.
    ggtheme : object
        Custom theme; defaults to ``theme_pubr()``.
    """
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

    # ---- Regression line with optional confidence band ----
    if add != "none":
        if isinstance(add, str):
            add = [add]
        for item in add:
            item_params = add_params.copy() if add_params else {}
            if item == "reg.line":
                if 'method' not in item_params:
                    item_params['method'] = 'lm'
                if 'se' not in item_params:
                    item_params['se'] = confint
                if confint_level != 0.95 and 'level' not in item_params:
                    item_params['level'] = confint_level
                p += geom_smooth(aes(**geom_mapping), **item_params)
            elif item in ("mean_se", "mean_sd"):
                group_col = color if color in df.columns else (fill if fill in df.columns else None)
                agg_df = df.groupby([x] + ([group_col] if group_col else []), as_index=False).agg(
                    mean_y=(y, 'mean'),
                    sd_y=(y, 'std'),
                    count_y=(y, 'count')
                )
                agg_df['se_y'] = agg_df['sd_y'] / np.sqrt(agg_df['count_y'].replace(0, np.nan))
                agg_df['se_y'] = agg_df['se_y'].fillna(0)
                agg_df['sd_y'] = agg_df['sd_y'].fillna(0)
                agg_df['ymin'] = agg_df['mean_y'] - (agg_df['se_y'] if item == "mean_se" else agg_df['sd_y'])
                agg_df['ymax'] = agg_df['mean_y'] + (agg_df['se_y'] if item == "mean_se" else agg_df['sd_y'])
                eb_mapping = aes(ymin='ymin', ymax='ymax')
                if group_col:
                    eb_mapping = aes(ymin='ymin', ymax='ymax', group=group_col)
                if 'width' not in item_params:
                    item_params['width'] = 0.2
                p += geom_errorbar(eb_mapping, data=agg_df,
                                   position=position if position else 'identity',
                                   **item_params)
            else:
                p = add_extra_layers(p, x, y, [item], add_params, df, color, fill)

    # ---- Confidence ellipse ----
    if ellipse:
        group_col = color if color in df.columns else (fill if fill in df.columns else None)
        ell_df = build_ellipse_df(df, x, y, group_col=group_col,
                                  level=ellipse_level, ellipse_type=ellipse_type)
        if len(ell_df) > 0:
            poly_mapping_dict = {"x": x, "y": y}
            if group_col and group_col in ell_df.columns:
                poly_mapping_dict["group"] = group_col
                poly_mapping_dict["fill"] = group_col
                poly_mapping_dict["color"] = group_col
            ell_params = {'alpha': ellipse_alpha, 'size': 0.8}
            p += geom_polygon(aes(**poly_mapping_dict), data=ell_df, **ell_params)
            if 'color' in geom_mapping:
                p += scale_color_pubr(palette)
            if 'fill' in geom_mapping:
                p += scale_fill_pubr(palette)

    # ---- Marginal rug plots ----
    if rug:
        # Vertical rug on x-axis
        x_vals = df[x].dropna().values
        if len(x_vals) > 0:
            y_range = df[y].dropna().values
            y_min, y_max = y_range.min(), y_range.max()
            rug_y = y_min - 0.02 * (y_max - y_min)
            rug_df_x = pd.DataFrame({x: x_vals, 'rug_y': rug_y})
            p += geom_point(aes(x=x, y='rug_y'), data=rug_df_x, shape='|',
                            size=rug_size, color='black', alpha=0.6)
        # Horizontal rug on y-axis
        y_vals = df[y].dropna().values
        if len(y_vals) > 0:
            x_range = df[x].dropna().values
            x_min, x_max = x_range.min(), x_range.max()
            rug_x = x_min - 0.02 * (x_max - x_min)
            rug_df_y = pd.DataFrame({y: y_vals, 'rug_x': rug_x})
            p += geom_point(aes(x='rug_x', y=y), data=rug_df_y, shape='_',
                            size=rug_size, color='black', alpha=0.6)

    # ---- Correlation annotation ----
    if cor:
        corr = compute_correlation(df[x].values, df[y].values, method=cor_method)
        if not np.isnan(corr['r']):
            if cor_coef:
                label_text = f"{corr['method_name']} R = {corr['r']:.3f}, R² = {corr['r2']:.3f}"
            else:
                p_str = _scipy_stats.chi2.sf(corr['r'] ** 2 * (len(df) - 2) / (1 - corr['r'] ** 2), df=1) \
                    if abs(corr['r']) < 1 else 0
                p_str = f"{p_str:.2g}" if not np.isnan(p_str) else "NA"
                label_text = f"{corr['method_name']} R = {corr['r']:.3f}, p = {p_str}"
            x_range = df[x].dropna().values
            y_range = df[y].dropna().values
            x_min, x_max = x_range.min(), x_range.max()
            y_min, y_max = y_range.min(), y_range.max()
            cor_x = x_min + 0.05 * (x_max - x_min)
            cor_y = y_max - 0.05 * (y_max - y_min)
            p += geom_text(x=cor_x, y=cor_y, label=label_text,
                           hjust=0, vjust=1, size=cor_size)

    # ---- Point labels ----
    if label is not None and label in df.columns:
        p += geom_text(aes(x=x, y=y, label=label), data=df,
                       size=label_size, color='black')

    # ---- Fixed aspect ratio ----
    if aspect_ratio is not None:
        p += coord_fixed(ratio=aspect_ratio)

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


# ==============================================================================
# ggqqplot — Q-Q plot for normality testing
# ==============================================================================

def ggqqplot(data, x, color="black", fill=None, palette="npg", shape=19, size=3,
              add="none", add_params=None,
              title=None, xlab=None, ylab=None,
              show_legend=True, ggtheme=None):
    """Create a publication-ready Q-Q plot to assess normality.

    Parameters
    ----------
    data : pd.DataFrame
        Input data.
    x : str
        Column name for the variable to test.
    color : str
        Column name or constant color for point outlines.
    fill : str
        Column name or constant color for point fills.
    palette : str
        Color palette name.
    shape : int
        Point shape.
    size : float
        Point size.
    add : str or list
        Additional layers: ``"qqline"`` for reference line.
    add_params : dict
        Extra parameters for the ``add`` layer.
    title, xlab, ylab : str
        Labels.
    show_legend : bool
        Whether to show the legend.
    ggtheme : object
        Custom theme.
    """
    df = data.copy()
    mapping = aes(sample=x)
    geom_mapping, geom_params = get_color_fill_aes_and_params(df, color, fill)

    p = ggplot(df, mapping)

    pt_params = {'shape': shape, 'size': size}
    pt_params.update(geom_params)
    p += geom_qq(aes(**geom_mapping), **pt_params)

    if add != "none":
        if isinstance(add, str):
            add = [add]
        for item in add:
            item_params = add_params.copy() if add_params else {}
            if item == "qqline" or item == "line":
                p += geom_qq_line(aes(**geom_mapping), **item_params)
            elif item == "qq2line" or item == "line2":
                p += geom_qq2_line(aes(**geom_mapping), **item_params)

    if 'color' in geom_mapping:
        p += scale_color_pubr(palette)
    if 'fill' in geom_mapping:
        p += scale_fill_pubr(palette)

    p = apply_labels_and_theme(p, title, xlab, ylab, None, show_legend, ggtheme)
    return p


# ==============================================================================
# ggecdf — Empirical cumulative distribution function plot
# ==============================================================================

def ggecdf(data, x, color="black", fill=None, palette="npg", size=1,
            stat="ecdf",
            title=None, xlab=None, ylab=None,
            show_legend=True, ggtheme=None):
    """Create a publication-ready ECDF (empirical CDF) plot.

    Parameters
    ----------
    data : pd.DataFrame
        Input data.
    x : str
        Column name for the variable.
    color : str
        Column name or constant color.
    fill : str
        Column name or constant color.
    palette : str
        Color palette name.
    size : float
        Line size.
    stat : str
        Statistic to use, default ``"ecdf"``.
    title, xlab, ylab : str
        Labels.
    show_legend : bool
        Whether to show the legend.
    ggtheme : object
        Custom theme.
    """
    df = data.copy()
    mapping = aes(x=x)
    geom_mapping, geom_params = get_color_fill_aes_and_params(df, color, fill)

    p = ggplot(df, mapping)

    ecdf_params = {'stat': stat}
    if size is not None:
        ecdf_params['size'] = size
    ecdf_params.update(geom_params)

    from lets_plot import geom_step
    p += geom_step(aes(**geom_mapping), **ecdf_params)

    if 'color' in geom_mapping:
        p += scale_color_pubr(palette)
    if 'fill' in geom_mapping:
        p += scale_fill_pubr(palette)

    p = apply_labels_and_theme(p, title, xlab, ylab, None, show_legend, ggtheme)
    return p


# ==============================================================================
# ggcorr — Correlation heatmap
# ==============================================================================

def _compute_correlation_matrix(df, method="pearson", digits=2, p_low="", p_high=""):
    """Compute a correlation matrix and p-value matrix.

    Returns (cor_df, p_df) where cor_df has correlation values and
    p_df has p-values, both in long format suitable for geom_tile.
    """
    var_cols = [c for c in df.columns if df[c].dtype in ('float64', 'int64', 'float32', 'int32')]
    n = len(var_cols)
    cor_matrix = np.zeros((n, n))
    p_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i == j:
                cor_matrix[i, j] = 1.0
                p_matrix[i, j] = np.nan
            else:
                x = df[var_cols[i]].values.astype(float)
                y = df[var_cols[j]].values.astype(float)
                mask = ~np.isnan(x) & ~np.isnan(y)
                x_clean, y_clean = x[mask], y[mask]
                if len(x_clean) < 3:
                    cor_matrix[i, j] = np.nan
                    p_matrix[i, j] = np.nan
                    continue

                method_lower = method.lower()
                if method_lower == "pearson":
                    r, p = _scipy_stats.pearsonr(x_clean, y_clean)
                elif method_lower == "spearman":
                    r, p = _scipy_stats.spearmanr(x_clean, y_clean)
                elif method_lower == "kendall":
                    r, p = _scipy_stats.kendalltau(x_clean, y_clean)
                else:
                    raise ValueError(f"Unknown correlation method: {method}")
                cor_matrix[i, j] = r
                p_matrix[i, j] = p

    rows = []
    p_rows = []
    for i in range(n):
        for j in range(n):
            val = cor_matrix[i, j]
            pval = p_matrix[i, j]
            if np.isnan(val):
                label = "NA"
            else:
                rounded = round(val, digits)
                if i == j:
                    label = str(rounded)
                elif not np.isnan(pval):
                    p_str = f"{pval:.2g}"
                    if p_low and pval < 0.05:
                        label = f"{rounded}\n{p_low}{p_str}"
                    elif p_high and pval >= 0.05:
                        label = f"{rounded}\n{p_high}{p_str}"
                    else:
                        label = str(rounded)
                else:
                    label = str(rounded)
            rows.append({"Var1": var_cols[i], "Var2": var_cols[j],
                          "cor": val, "label": label})
            p_rows.append({"Var1": var_cols[i], "Var2": var_cols[j],
                           "p": pval})

    cor_df = pd.DataFrame(rows)
    p_df = pd.DataFrame(p_rows)
    return cor_df, p_df, var_cols


def ggcorr(data, method="pearson", digits=2, p_low="", p_high="",
            cor_mat=None, p_mat=None,
            title=None, show_legend=True, ggtheme=None):
    """Create a publication-ready correlation heatmap.

    Parameters
    ----------
    data : pd.DataFrame
        Input data (numeric columns will be used).
    method : str
        Correlation method: ``"pearson"``, ``"spearman"``, or ``"kendall"``.
    digits : int
        Number of decimal places for correlation labels.
    p_low : str
        Symbol prefix for p < 0.05 (e.g. ``"*"``).
    p_high : str
        Symbol prefix for p >= 0.05 (e.g. ``"ns"``).
    cor_mat : pd.DataFrame, optional
        Pre-computed correlation matrix in long format.
    p_mat : pd.DataFrame, optional
        Pre-computed p-value matrix in long format.
    title : str
        Plot title.
    show_legend : bool
        Whether to show the legend.
    ggtheme : object
        Custom theme.
    """
    if cor_mat is None:
        cor_df, p_df, var_cols = _compute_correlation_matrix(
            data, method=method, digits=digits,
            p_low=p_low, p_high=p_high
        )
    else:
        cor_df = cor_mat
        var_cols = sorted(set(cor_df["Var1"].unique()) | set(cor_df["Var2"].unique()))

    mapping = aes(x="Var1", y="Var2", fill="cor")
    p = ggplot(cor_df, mapping)

    p += geom_tile(aes(x="Var1", y="Var2", fill="cor"), color="white", size=0.5)

    p += geom_text(aes(x="Var1", y="Var2", label="label"),
                   data=cor_df, color="black", size=4)

    p += scale_fill_gradient2(low="#B2182B", mid="#F7F7F7", high="#2166AC",
                              midpoint=0, limits=[-1, 1])

    p += scale_x_discrete(limits=var_cols)
    p += scale_x_discrete(limits=var_cols)

    theme_obj = ggtheme if ggtheme is not None else theme_pubr()
    if not show_legend:
        theme_obj += theme(legend_position='none')
    p += theme_obj

    if title:
        p += ggtitle(title)

    return p


# ==============================================================================
# rremove — Remove plot elements
# ==============================================================================

def rremove(plot, what):
    """Remove plot elements (axes, titles, legends, etc.).

    Parameters
    ----------
    plot : PlotSpec
        The plot to modify.
    what : str
        Element to remove. One of:
        - ``"title"``, ``"subtitle"``
        - ``"xlab"``, ``"ylab"``
        - ``"x.text"``, ``"y.text"`` (axis tick labels)
        - ``"x.ticks"``, ``"y.ticks"`` (axis tick marks)
        - ``"x.axis"``, ``"y.axis"`` (axis lines)
        - ``"axis"`` (both axes)
        - ``"legend"``, ``"legend.title"``
        - ``"grid"``
        - ``"panel.grid"``
    """
    theme_mods = {}
    what_lower = what.lower()

    if what_lower in ("title", "plot.title"):
        return plot + theme(plot_title="blank")
    elif what_lower in ("subtitle", "plot.subtitle"):
        return plot + theme(plot_subtitle="blank")
    elif what_lower in ("xlab", "axis.title.x"):
        return plot + theme(axis_title_x="blank")
    elif what_lower in ("ylab", "axis.title.y"):
        return plot + theme(axis_title_y="blank")
    elif what_lower in ("x.text", "axis.text.x"):
        return plot + theme(axis_text_x="blank")
    elif what_lower in ("y.text", "axis.text.y"):
        return plot + theme(axis_text_y="blank")
    elif what_lower in ("x.ticks", "axis.ticks.x"):
        return plot + theme(axis_ticks_x="blank")
    elif what_lower in ("y.ticks", "axis.ticks.y"):
        return plot + theme(axis_ticks_y="blank")
    elif what_lower in ("x.axis", "axis.line.x"):
        return plot + theme(axis_line_x="blank")
    elif what_lower in ("y.axis", "axis.line.y"):
        return plot + theme(axis_line_y="blank")
    elif what_lower == "axis":
        return plot + theme(
            axis_line_x="blank", axis_line_y="blank",
            axis_ticks_x="blank", axis_ticks_y="blank",
            axis_title_x="blank", axis_title_y="blank",
            axis_text_x="blank", axis_text_y="blank"
        )
    elif what_lower in ("legend", "legend.position"):
        return plot + theme(legend_position="none")
    elif what_lower == "legend.title":
        return plot + theme(legend_title="blank")
    elif what_lower in ("grid", "panel.grid"):
        return plot + theme(panel_grid_major="blank", panel_grid_minor="blank")
    elif what_lower in ("panel", "panel.background"):
        return plot + theme(panel_background="blank")
    else:
        raise ValueError(f"Unknown element to remove: {what}")


# ==============================================================================
# ggpar — Generic plot modifier
# ==============================================================================

def ggpar(plot, title=None, xlab=None, ylab=None,
          font_main=None, font_x=None, font_y=None,
          legend=None, legend_title=None,
          palette=None,
          show_legend=None,
          font_size=None):
    """Customize an existing plot's appearance.

    Parameters
    ----------
    plot : PlotSpec
        The plot to modify.
    title : str
        New title.
    xlab : str
        New x-axis label.
    ylab : str
        New y-axis label.
    font_main : int
        Title font size.
    font_x : int
        X-axis label font size.
    font_y : int
        Y-axis label font size.
    legend : str
        Legend position: ``"right"``, ``"left"``, ``"top"``, ``"bottom"``, ``"none"``.
    legend_title : str
        Legend title text.
    palette : str
        Color palette name to apply.
    show_legend : bool
        Whether to show the legend.
    font_size : int
        Base font size.
    """
    if title is not None:
        plot = plot + ggtitle(title)
    if xlab is not None:
        plot = plot + _xlab(xlab)
    if ylab is not None:
        plot = plot + _ylab(ylab)

    if palette is not None:
        plot = plot + scale_color_pubr(palette) + scale_fill_pubr(palette)

    if show_legend is False:
        plot = plot + theme(legend_position="none")
    elif legend is not None:
        plot = plot + theme(legend_position=legend)

    if legend_title is not None:
        plot = plot + theme(legend_title=legend_title)

    theme_args = {}
    if font_size is not None:
        theme_args["base_size"] = font_size

    if theme_args:
        base_theme = theme_pubr(**theme_args)
        plot = plot + base_theme

    return plot


# ==============================================================================
# ggheatmap / ggclustergram / ggclustervis — Publication-ready Clustered Heatmap
# ==============================================================================

def ggheatmap(data, x=None, y=None, fill=None,
              scale="none",
              cluster_rows=False, cluster_cols=False,
              metric="euclidean", method="complete",
              palette="bwr", low=None, mid=None, high=None, midpoint=0,
              show_values=False, digits=2, value_color="black", value_size=3,
              cell_border="white", cell_size=0.5,
              title=None, xlab=None, ylab=None,
              show_legend=True, ggtheme=None):
    """Create a publication-ready heatmap with optional hierarchical clustering and scaling.

    Parameters
    ----------
    data : pd.DataFrame
        Matrix DataFrame (index=rows, columns=cols) or long-format DataFrame with x, y, fill columns.
    x : str, optional
        Column name for X axis (columns) if data is in long format.
    y : str, optional
        Column name for Y axis (rows) if data is in long format.
    fill : str, optional
        Column name for cell values if data is in long format.
    scale : str
        Data scaling: ``"none"``, ``"row"`` (row z-score), or ``"column"`` (column z-score).
    cluster_rows : bool
        Whether to hierarchically cluster rows.
    cluster_cols : bool
        Whether to hierarchically cluster columns.
    metric : str
        Distance metric for scipy pdist (e.g., ``"euclidean"``, ``"correlation"``, ``"cosine"``).
    method : str
        Linkage method for scipy linkage (e.g., ``"complete"``, ``"ward"``, ``"average"``).
    palette : str
        Color scheme: ``"bwr"`` (blue-white-red), ``"npg"``, ``"coolwarm"``, ``"rdbu"``, ``"nejm"``, ``"viridis"``, ``"magma"``, ``"plasma"``.
    low, mid, high : str, optional
        Custom colors for lower, middle, and upper gradient bounds.
    midpoint : float
        Midpoint value for diverging color gradients (default 0).
    show_values : bool
        Whether to render numeric text values inside heatmap cells.
    digits : int
        Decimal places for displayed values.
    value_color : str
        Color of value text labels.
    value_size : float
        Font size of value text labels.
    cell_border : str
        Color of cell border lines.
    cell_size : float
        Thickness of cell border lines.
    title, xlab, ylab : str, optional
        Labels for plot.
    show_legend : bool
        Whether to display legend.
    ggtheme : object, optional
        Custom theme.
    """
    df_raw = data.copy()

    # Convert long format to wide matrix if x, y, fill provided
    if x is not None and y is not None and fill is not None:
        mat = df_raw.pivot(index=y, columns=x, values=fill)
    else:
        # Matrix DataFrame
        mat = df_raw.select_dtypes(include=[np.number]).copy()

    # Standardize / Scale
    if scale == "row":
        mean = mat.mean(axis=1)
        std = mat.std(axis=1).replace(0, 1)
        mat = mat.sub(mean, axis=0).div(std, axis=0)
    elif scale == "column":
        mean = mat.mean(axis=0)
        std = mat.std(axis=0).replace(0, 1)
        mat = mat.sub(mean, axis=1).div(std, axis=1)
    elif scale != "none":
        raise ValueError(f"Unknown scale option: '{scale}'. Choose 'none', 'row', or 'column'.")

    # Row Clustering
    row_order = mat.index.tolist()
    if cluster_rows and mat.shape[0] > 1:
        row_dists = _pdist(mat.values, metric=metric)
        row_linkage = _linkage(row_dists, method=method)
        row_dendro = _dendrogram(row_linkage, no_plot=True)
        row_order = [mat.index[i] for i in row_dendro['leaves']]

    # Column Clustering
    col_order = mat.columns.tolist()
    if cluster_cols and mat.shape[1] > 1:
        col_dists = _pdist(mat.values.T, metric=metric)
        col_linkage = _linkage(col_dists, method=method)
        col_dendro = _dendrogram(col_linkage, no_plot=True)
        col_order = [mat.columns[i] for i in col_dendro['leaves']]

    # Reorder matrix
    mat_ordered = mat.loc[row_order, col_order]

    if mat_ordered.index.name is None:
        mat_ordered.index.name = 'Row'
    row_col_name = mat_ordered.index.name
    # Convert to long format for geom_tile
    long_df = mat_ordered.reset_index().melt(id_vars=row_col_name,
                                             var_name='Col',
                                             value_name='Value')
    long_df['label_str'] = long_df['Value'].apply(lambda v: f"{v:.{digits}f}" if pd.notnull(v) else "")

    # Build plot
    mapping = aes(x='Col', y=row_col_name, fill='Value')
    p = ggplot(long_df, mapping)

    tile_params = {'width': 1.0, 'height': 1.0}
    if cell_border:
        tile_params['color'] = cell_border
    if cell_size:
        tile_params['size'] = cell_size

    p += geom_tile(aes(x='Col', y=row_col_name, fill='Value'), **tile_params)

    if show_values:
        p += geom_text(aes(x='Col', y=row_col_name, label='label_str'),
                       color=value_color, size=value_size)

    # Color palettes
    if low or mid or high:
        c_low = low or "#2166AC"
        c_mid = mid or "#F7F7F7"
        c_high = high or "#B2182B"
        p += scale_fill_gradient2(low=c_low, mid=c_mid, high=c_high, midpoint=midpoint)
    elif palette == "bwr" or palette == "rdbu":
        p += scale_fill_gradient2(low="#2166AC", mid="#F7F7F7", high="#B2182B", midpoint=midpoint)
    elif palette == "npg" or palette == "coolwarm":
        p += scale_fill_gradient2(low="#3C5488", mid="#F7F7F7", high="#E64B35", midpoint=midpoint)
    elif palette == "nejm":
        p += scale_fill_gradient2(low="#0072B5", mid="#F7F7F7", high="#BC3C29", midpoint=midpoint)
    elif palette in ("viridis", "magma", "plasma"):
        from lets_plot import scale_fill_viridis
        p += scale_fill_viridis(option=palette)
    else:
        p += scale_fill_gradient2(low="#2166AC", mid="#F7F7F7", high="#B2182B", midpoint=midpoint)

    p += scale_x_discrete(limits=col_order, expand=[0, 0])
    p += scale_y_discrete(limits=row_order, expand=[0, 0])

    theme_obj = ggtheme if ggtheme is not None else theme_pubr()
    if not show_legend:
        theme_obj += theme(legend_position='none')

    p += theme_obj

    if title:
        p += ggtitle(title)
    if xlab:
        p += _xlab(xlab)
    if ylab:
        p += _ylab(ylab)

    return p


def ggclustergram(data, scale="row", cluster_rows=True, cluster_cols=True, **kwargs):
    """Create a publication-ready clustered heatmap (clustergram / clustervis)."""
    return ggheatmap(data, scale=scale, cluster_rows=cluster_rows, cluster_cols=cluster_cols, **kwargs)

ggclustervis = ggclustergram
ggheatmap_cluster = ggclustergram


# ==============================================================================
# visCluster / ggvisCluster — ClusterGVis-style dual view (Heatmap + Trend Lines)
# ==============================================================================

def visCluster(data,
               n_clusters=4,
               scale="row",
               plot_type="both",
               trend_position="left",
               cluster_method="hierarchical",
               palette="bwr",
               cluster_palette="npg",
               metric="euclidean",
               method="ward",
               title=None,
               xlab=None,
               ylab=None,
               show_legend=True,
               ggtheme=None):
    """ClusterGVis-style cluster visualization combining heatmaps and cluster expression trend lines.

    Parameters
    ----------
    data : pd.DataFrame
        Matrix DataFrame (index=genes/rows, columns=samples/timepoints).
    n_clusters : int
        Number of cluster groups (default 4).
    scale : str
        Scaling method: ``"row"`` (z-score), ``"column"``, or ``"none"``.
    plot_type : str
        Visualization layout: ``"both"`` (heatmap + line plot side-by-side), ``"heatmap"``, or ``"line"``.
    cluster_method : str
        Clustering algorithm: ``"hierarchical"`` or ``"kmeans"``.
    palette : str
        Heatmap palette name (e.g. ``"bwr"``, ``"coolwarm"``, ``"npg"``, ``"nejm"``).
    cluster_palette : str
        Palette for cluster trend lines (e.g. ``"npg"``, ``"aaas"``, ``"jco"``).
    metric : str
        Distance metric for scipy pdist (e.g., ``"euclidean"``, ``"correlation"``).
    method : str
        Linkage method for scipy linkage (e.g., ``"ward"``, ``"complete"``, ``"average"``).
    title, xlab, ylab : str, optional
        Plot labels.
    show_legend : bool
        Whether to show legend.
    ggtheme : object, optional
        Custom theme.
    """
    df_raw = data.select_dtypes(include=[np.number]).copy()
    if df_raw.shape[1] > 150:
        n_bins = 100
        cell_cols = df_raw.columns
        chunks = np.array_split(cell_cols, n_bins)
        binned_data = {}
        for idx, chunk in enumerate(chunks):
            binned_data[f'Pt_{idx+1:03d}'] = df_raw[chunk].mean(axis=1)
        df_raw = pd.DataFrame(binned_data)

    # Standardize / Scale
    if scale == "row":
        mean = df_raw.mean(axis=1)
        std = df_raw.std(axis=1).replace(0, 1)
        mat = df_raw.sub(mean, axis=0).div(std, axis=0)
    elif scale == "column":
        mean = df_raw.mean(axis=0)
        std = df_raw.std(axis=0).replace(0, 1)
        mat = df_raw.sub(mean, axis=1).div(std, axis=1)
    else:
        mat = df_raw.copy()

    # Cluster assignment
    if mat.shape[0] >= n_clusters:
        row_dists = _pdist(mat.values, metric=metric)
        row_linkage = _linkage(row_dists, method=method)
        clusters = _fcluster(row_linkage, t=n_clusters, criterion='maxclust')
    else:
        clusters = np.arange(1, mat.shape[0] + 1)

    mat['Cluster'] = [f'C{c}' for c in clusters]
    df_sorted = mat.sort_values(by='Cluster')
    col_names = [c for c in df_sorted.columns if c != 'Cluster']

    # Build Heatmap
    p_heat = None
    if plot_type in ("both", "heatmap"):
        df_heat_mat = df_sorted.drop(columns=['Cluster'])
        reset_heat = df_heat_mat.reset_index()
        gene_col = 'index' if 'index' in reset_heat.columns else df_heat_mat.index.name or 'index'
        long_heat = reset_heat.melt(id_vars=gene_col, var_name='Timepoint', value_name='Expression')
        long_heat.rename(columns={gene_col: 'Gene'}, inplace=True)
        long_heat['Cluster'] = long_heat['Gene'].map(mat['Cluster'])
        long_heat['Gene'] = pd.Categorical(long_heat['Gene'], categories=df_sorted.index.tolist(), ordered=True)

        p_heat = ggplot(long_heat, aes(x='Timepoint', y='Gene', fill='Expression'))
        p_heat += geom_tile(width=1.0, height=1.0, color='white', size=0.2)

        if palette in ("bwr", "rdbu"):
            p_heat += scale_fill_gradient2(low="#2166AC", mid="#F7F7F7", high="#B2182B", midpoint=0)
        elif palette in ("npg", "coolwarm"):
            p_heat += scale_fill_gradient2(low="#3C5488", mid="#F7F7F7", high="#E64B35", midpoint=0)
        elif palette == "nejm":
            p_heat += scale_fill_gradient2(low="#0072B5", mid="#F7F7F7", high="#BC3C29", midpoint=0)
        else:
            p_heat += scale_fill_gradient2(low="#2166AC", mid="#F7F7F7", high="#B2182B", midpoint=0)

        p_heat += scale_x_discrete(limits=col_names, expand=[0, 0])
        p_heat += scale_y_discrete(expand=[0, 0])
        p_heat += facet_grid(y='Cluster', scales='free_y')

        theme_h = ggtheme if ggtheme is not None else theme_pubr()
        if not show_legend:
            theme_h += theme(legend_position='none')
        p_heat += theme_h
        if title:
            p_heat += ggtitle(f"{title} - Heatmap")
        if xlab:
            p_heat += _xlab(xlab)
        if ylab:
            p_heat += _ylab(ylab)

    # Build Line Trend Plot
    p_line = None
    if plot_type in ("both", "line"):
        reset_mat = mat.reset_index()
        gene_col_name = 'index' if 'index' in reset_mat.columns else mat.index.name or 'Gene'
        if gene_col_name in reset_mat.columns:
            reset_mat.rename(columns={gene_col_name: 'Gene'}, inplace=True)
            gene_col_name = 'Gene'

        long_line = reset_mat.melt(id_vars=[gene_col_name, 'Cluster'], var_name='Timepoint', value_name='Expression')

        agg_df = long_line.groupby(['Cluster', 'Timepoint'], as_index=False).agg(
            mean_val=('Expression', 'mean'),
            sd_val=('Expression', 'std')
        )
        agg_df['sd_val'] = agg_df['sd_val'].fillna(0)
        agg_df['ymin'] = agg_df['mean_val'] - agg_df['sd_val']
        agg_df['ymax'] = agg_df['mean_val'] + agg_df['sd_val']

        p_line = ggplot(agg_df, aes(x='Timepoint', y='mean_val', group='Cluster', color='Cluster', fill='Cluster'))
        p_line += geom_ribbon(aes(ymin='ymin', ymax='ymax'), alpha=0.2, color='blank')
        p_line += geom_line(size=1.2)
        p_line += geom_point(size=2.5)
        p_line += scale_x_discrete(limits=col_names)
        p_line += facet_grid(y='Cluster', scales='free_y')

        theme_l = ggtheme if ggtheme is not None else theme_pubr()
        if not show_legend:
            theme_l += theme(legend_position='none')
        p_line += theme_l
        p_line += scale_color_pubr(cluster_palette)
        p_line += scale_fill_pubr(cluster_palette)
        if title:
            p_line += ggtitle(f"{title} - Trends")
        if xlab:
            p_line += _xlab(xlab)
        p_line += _ylab("Expression (Mean ± SD)")

    if plot_type == "overlay":
        df_heat_mat = df_sorted.drop(columns=['Cluster'])
        reset_heat = df_heat_mat.reset_index()
        gene_col = 'index' if 'index' in reset_heat.columns else df_heat_mat.index.name or 'index'
        long_heat = reset_heat.melt(id_vars=gene_col, var_name='Timepoint', value_name='Expression')
        long_heat.rename(columns={gene_col: 'Gene'}, inplace=True)
        long_heat['Cluster'] = long_heat['Gene'].map(mat['Cluster'])
        long_heat['Gene'] = pd.Categorical(long_heat['Gene'], categories=df_sorted.index.tolist(), ordered=True)

        agg_df = long_heat.groupby(['Cluster', 'Timepoint'], as_index=False).agg(mean_val=('Expression', 'mean'))

        cluster_overlay_lines = []
        for c_id, group in df_sorted.groupby('Cluster'):
            gene_list = group.index.tolist()
            c_agg = agg_df[agg_df['Cluster'] == c_id].copy()
            vals = c_agg['mean_val'].values
            min_v, max_v = vals.min(), vals.max()
            rng = (max_v - min_v) if max_v != min_v else 1.0
            indices = [gene_list[int(round(idx))] for idx in (vals - min_v) / rng * (len(gene_list) - 1)]
            c_agg['Gene'] = pd.Categorical(indices, categories=df_sorted.index.tolist(), ordered=True)
            cluster_overlay_lines.append(c_agg)

        df_trend_overlay = pd.concat(cluster_overlay_lines)

        p_overlay = ggplot()
        p_overlay += geom_tile(data=long_heat, mapping=aes(x='Timepoint', y='Gene', fill='Expression'),
                               width=1.0, height=1.0, color='white', size=0.2)
        p_overlay += geom_line(data=df_trend_overlay, mapping=aes(x='Timepoint', y='Gene', group='Cluster'),
                                color='black', size=2.5)
        p_overlay += geom_line(data=df_trend_overlay, mapping=aes(x='Timepoint', y='Gene', group='Cluster'),
                                color='#FFD700', size=1.2)
        p_overlay += geom_point(data=df_trend_overlay, mapping=aes(x='Timepoint', y='Gene'),
                                 color='#FFD700', size=3.5)

        if palette in ("bwr", "rdbu"):
            p_overlay += scale_fill_gradient2(low="#2166AC", mid="#F7F7F7", high="#B2182B", midpoint=0)
        elif palette in ("npg", "coolwarm"):
            p_overlay += scale_fill_gradient2(low="#3C5488", mid="#F7F7F7", high="#E64B35", midpoint=0)
        elif palette == "nejm":
            p_overlay += scale_fill_gradient2(low="#0072B5", mid="#F7F7F7", high="#BC3C29", midpoint=0)
        else:
            p_overlay += scale_fill_gradient2(low="#2166AC", mid="#F7F7F7", high="#B2182B", midpoint=0)

        p_overlay += scale_x_discrete(limits=col_names, expand=[0, 0])
        p_overlay += scale_y_discrete(expand=[0, 0])
        p_overlay += facet_grid(y='Cluster', scales='free_y')

        theme_o = ggtheme if ggtheme is not None else theme_pubr()
        if not show_legend:
            theme_o += theme(legend_position='none')
        p_overlay += theme_o
        if title:
            p_overlay += ggtitle(title)
        if xlab:
            p_overlay += _xlab(xlab)
        if ylab:
            p_overlay += _ylab(ylab)

        return p_overlay

    if plot_type == "joined":
        df_heat_mat = df_sorted.drop(columns=['Cluster'])
        reset_heat = df_heat_mat.reset_index()
        gene_col = 'index' if 'index' in reset_heat.columns else df_heat_mat.index.name or 'index'
        long_heat = reset_heat.melt(id_vars=gene_col, var_name='Timepoint', value_name='Expression')
        long_heat.rename(columns={gene_col: 'Gene'}, inplace=True)
        long_heat['Cluster'] = long_heat['Gene'].map(mat['Cluster'])
        long_heat['Gene'] = pd.Categorical(long_heat['Gene'], categories=df_sorted.index.tolist(), ordered=True)

        trend_cols = [f'T_{tp}' for tp in col_names]
        all_x_limits = trend_cols + col_names + ['gap_x', 'Cluster', 'end_x']
        x_labels = col_names + col_names + ['', 'Cluster', '']

        long_heat['X_pos'] = long_heat['Timepoint']

        df_cluster_bar = pd.DataFrame({
            'Gene': pd.Categorical(df_sorted.index.tolist(), categories=df_sorted.index.tolist(), ordered=True),
            'Cluster': df_sorted['Cluster'].values,
            'X_pos': 'Cluster'
        })

        agg_df = long_heat.groupby(['Cluster', 'Timepoint'], as_index=False).agg(mean_val=('Expression', 'mean'))

        cluster_overlay_lines = []
        for c_id, group in df_sorted.groupby('Cluster'):
            gene_list = group.index.tolist()
            c_agg = agg_df[agg_df['Cluster'] == c_id].copy()
            vals = c_agg['mean_val'].values
            min_v, max_v = vals.min(), vals.max()
            rng = (max_v - min_v) if max_v != min_v else 1.0
            indices = [gene_list[int(round(idx))] for idx in (vals - min_v) / rng * (len(gene_list) - 1)]
            c_agg['Gene'] = pd.Categorical(indices, categories=df_sorted.index.tolist(), ordered=True)
            c_agg['X_pos'] = c_agg['Timepoint'].apply(lambda tp: f'T_{tp}')
            cluster_overlay_lines.append(c_agg)

        df_trend_left = pd.concat(cluster_overlay_lines)

        trend_box_rows = []
        for c_id, group in df_sorted.groupby('Cluster'):
            gene_list = group.index.tolist()
            first_g, last_g = gene_list[0], gene_list[-1]
            trend_box_rows.append({'Cluster': c_id, 'xmin': trend_cols[0], 'xmax': trend_cols[-1], 'ymin': first_g, 'ymax': last_g})
        df_trend_box = pd.DataFrame(trend_box_rows)

        p_joined = ggplot()
        is_dense_cols = len(col_names) >= 15
        if is_dense_cols:
            p_joined += geom_tile(data=long_heat, mapping=aes(x='X_pos', y='Gene', fill='Expression'),
                                  width=1.05, height=1.05)
        else:
            p_joined += geom_tile(data=long_heat, mapping=aes(x='X_pos', y='Gene', fill='Expression'),
                                  width=1.0, height=1.0, color='white', size=0.2)

        p_joined += geom_point(data=df_cluster_bar, mapping=aes(x='X_pos', y='Gene', color='Cluster'),
                                shape=15, size=26.0)

        cluster_text_rows = []
        for c_id, group in df_sorted.groupby('Cluster'):
            g_list = group.index.tolist()
            mid_g = g_list[len(g_list) // 2]
            cluster_text_rows.append({
                'Gene': mid_g,
                'Cluster': c_id,
                'X_pos': 'Cluster',
                'Text': c_id
            })
        df_cluster_text = pd.DataFrame(cluster_text_rows)
        df_cluster_text['Gene'] = pd.Categorical(df_cluster_text['Gene'], categories=df_sorted.index.tolist(), ordered=True)

        p_joined += geom_text(data=df_cluster_text, mapping=aes(x='X_pos', y='Gene', label='Text'),
                               color='white', size=11, fontface='bold', angle=90)

        p_joined += geom_line(data=df_trend_left, mapping=aes(x='X_pos', y='Gene', group='Cluster', color='Cluster'),
                               size=3.0 if is_dense_cols else 2.5)
        if not is_dense_cols:
            p_joined += geom_point(data=df_trend_left, mapping=aes(x='X_pos', y='Gene', color='Cluster'),
                                    size=4.0)

        # Independent border box around left trend line for each cluster
        p_joined += geom_rect(data=df_trend_box, mapping=aes(xmin='xmin', xmax='xmax', ymin='ymin', ymax='ymax'),
                              color='black', fill='#00000000', size=0.8)

        if palette in ("bwr", "rdbu"):
            p_joined += scale_fill_gradient2(low="#2166AC", mid="#F7F7F7", high="#B2182B", midpoint=0)
        elif palette in ("npg", "coolwarm"):
            p_joined += scale_fill_gradient2(low="#3C5488", mid="#F7F7F7", high="#E64B35", midpoint=0)
        elif palette == "nejm":
            p_joined += scale_fill_gradient2(low="#0072B5", mid="#F7F7F7", high="#BC3C29", midpoint=0)
        else:
            p_joined += scale_fill_gradient2(low="#2166AC", mid="#F7F7F7", high="#B2182B", midpoint=0)

        p_joined += scale_color_pubr(cluster_palette)
        p_joined += scale_x_discrete(limits=all_x_limits, labels=x_labels, expand=[0, 0])
        p_joined += scale_y_discrete(expand=[0, 0])
        p_joined += facet_grid(y='Cluster', scales='free_y')

        theme_j = ggtheme if ggtheme is not None else theme_pubr()
        theme_j += theme(
            strip_text=element_blank(),
            strip_background=element_blank(),
            panel_background=element_rect(color='black', fill='#00000000', size=0.8),
            axis_text_x=element_blank(),
            axis_ticks_x=element_blank()
        )
        if len(df_sorted) > 50:
            theme_j += theme(axis_text_y=element_blank(), axis_ticks_y=element_blank())
        if not show_legend:
            theme_j += theme(legend_position='none')
        p_joined += theme_j
        if title:
            p_joined += ggtitle(title)
        if xlab:
            p_joined += _xlab(xlab)
        if ylab:
            p_joined += _ylab(ylab)

        return p_joined

    if plot_type == "heatmap":
        return p_heat
    elif plot_type == "line":
        return p_line
    else:
        from .arrange import ggarrange
        if trend_position == "left":
            return ggarrange(p_line, p_heat, ncol=2, common_legend=False)
        else:
            return ggarrange(p_heat, p_line, ncol=2, common_legend=False)

ggvisCluster = visCluster


def sim_pseudotime_data(n_genes=80, n_pts=50, n_clusters=4, seed=42):
    """
    Simulate single-cell RNA-seq pseudotime trajectory gene expression matrix with customizable n_clusters (包含可自定义聚类数量).
    Useful for Monocle-style pseudotime heatmaps (拟时序热图).
    """
    np.random.seed(seed)
    t = np.linspace(0, 100, n_pts)
    n_clusters = max(1, int(n_clusters))
    genes_per_cluster = max(1, n_genes // n_clusters)
    
    data = []
    gene_names = []
    filter_sigma = max(2.0, n_pts / 25.0)
    sigma_width = 220.0 / (n_clusters ** 0.7)
    
    for c_idx in range(1, n_clusters + 1):
        center = (c_idx - 1) / max(1, n_clusters - 1) * 100.0
        
        for i in range(genes_per_cluster):
            jitter_center = center + np.random.uniform(-4, 4)
            if c_idx == 1:
                # Early response / Stemness (Decaying)
                pattern = np.exp(-t / (16 + np.random.uniform(-3, 3)))
                prefix = 'Early'
            elif c_idx == n_clusters:
                # Late terminal differentiation (Rising)
                pattern = 1.0 / (1.0 + np.exp(-(t - (78 + np.random.uniform(-4, 4))) / 10.0))
                prefix = 'Late'
            else:
                # Mid transition pulse peak
                pattern = np.exp(-((t - jitter_center)**2) / sigma_width)
                prefix = f'Mid{c_idx-1}'
                
            noise = np.random.normal(0, 0.05, n_pts)
            smooth_curve = _gaussian_filter1d(pattern + noise, sigma=filter_sigma)
            data.append(smooth_curve)
            gene_names.append(f'{prefix}_Gene_{i+1:04d}')

    if n_pts > 200:
        col_names = [f'Cell_{i+1:04d}' for i in range(n_pts)]
    else:
        col_names = [f'Pt_{int(pt)}' for pt in t]
    df = pd.DataFrame(data, index=gene_names, columns=col_names)
    return df

sim_pseudotime = sim_pseudotime_data


def visPseudotime(
    data=None,
    n_clusters=4,
    scale='row',
    plot_type='joined',
    cluster_palette='npg',
    palette='bwr',
    title='Monocle Single-Cell Pseudotime Trajectory Heatmap',
    xlab='Pseudotime Continuum (Cell Differentiation)',
    ylab='Gene',
    **kwargs
):
    """
    Visualize single-cell RNA-seq pseudotime trajectory heatmaps (拟时序热图).
    If data is None, automatically simulates high-quality pseudotime data using sim_pseudotime_data().
    """
    if data is None:
        data = sim_pseudotime_data(n_genes=80, n_pts=40, n_clusters=n_clusters)
        
    return visCluster(
        data,
        n_clusters=n_clusters,
        scale=scale,
        plot_type=plot_type,
        cluster_palette=cluster_palette,
        palette=palette,
        title=title,
        xlab=xlab,
        ylab=ylab,
        **kwargs
    )

ggpseudotime = visPseudotime


# ==============================================================================
# GSEA Visualization (gseapyvis Migration)
# ==============================================================================

def sim_gsea_data(n_genes=100, n_hits=12, nes=1.85, pval=0.001, fdr=0.005, term="KEGG_CELL_CYCLE", seed=42):
    """
    Simulate synthetic GSEA prerank result dict and rnk dataframe for demonstration.
    Returns (res_data, term, rnk).
    """
    np.random.seed(seed)
    steps = np.random.randn(n_genes)
    steps[:n_hits*2] += 0.4
    res = np.cumsum(steps)
    res = res - res.min() + 0.05
    
    hits = sorted(np.random.choice(int(n_genes * 0.4), size=n_hits, replace=False).tolist())
    gene_names = [f"Gene_{i+1:03d}" for i in range(n_genes)]
    matched = ";".join(gene_names[h] for h in hits)
    
    res_data = {
        term: {
            "RES": res.tolist(),
            "hits": hits,
            "nes": nes,
            "pval": pval,
            "fdr": fdr,
            "matched_genes": matched
        }
    }
    
    scores = np.sort(np.random.randn(n_genes))[::-1]
    rnk = pd.DataFrame({"gene": gene_names, "score": scores})
    
    return res_data, term, rnk


def _hex_to_rgb(hex_str):
    color_map = {
        'red': '#FF0000', 'blue': '#0000FF', 'white': '#FFFFFF',
        'green': '#00FF00', 'black': '#000000', 'yellow': '#FFFF00'
    }
    hex_str = color_map.get(str(hex_str).lower(), str(hex_str)).lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    return np.array([int(hex_str[i:i+2], 16) for i in (0, 2, 4)], dtype=float)

def _rgb_to_hex(rgb):
    rgb_clamped = np.clip(rgb, 0, 255)
    return '#{:02x}{:02x}{:02x}'.format(int(round(rgb_clamped[0])), int(round(rgb_clamped[1])), int(round(rgb_clamped[2])))

def _get_gradient_10(col1='red', col2='blue'):
    rgb1 = _hex_to_rgb(col1)
    white = _hex_to_rgb('white')
    rgb2 = _hex_to_rgb(col2)
    half1 = [rgb1 + (white - rgb1) * (i / 4.0) for i in range(5)]
    half2 = [white + (rgb2 - white) * (i / 4.0) for i in range(5)]
    return [_rgb_to_hex(rgb) for rgb in (half1 + half2)]


def compute_heat_blocks(gsdata, htCol=("red", "blue"), htHeight=1.0):
    """Compute color gradient heatmap blocks for GSEA hit positions."""
    all_blocks = []
    for setid in gsdata["Description"].unique():
        tmp = gsdata[gsdata["Description"] == setid].copy()

        rev_pos = tmp["position"].values[::-1]
        rev_cumsum = np.cumsum(rev_pos)

        v = np.linspace(1, rev_pos.sum(), 9)
        inv = np.searchsorted(v, rev_cumsum, side="right")

        if inv.min() == 0:
            inv += 1

        tmp = tmp.reset_index(drop=True)
        tmp["inv"] = inv

        tmp["group"] = (tmp["inv"] != tmp["inv"].shift()).cumsum()

        for _, g in tmp.groupby("group"):
            xmin = g.index.min()
            xmax = g.index.max() + 1
            color_idx = g["inv"].iloc[0]
            all_blocks.append({
                "xmin": xmin,
                "xmax": xmax,
                "ymin": 0,
                "ymax": htHeight,
                "col": color_idx,
                "Description": setid
            })

    color_list = _get_gradient_10(htCol[0], htCol[1])

    block_df = pd.DataFrame(all_blocks)
    block_df["col"] = block_df["col"] - 1
    block_df["col"] = block_df["col"].apply(lambda i: color_list[min(i, len(color_list)-1)])

    return block_df


def gsea_plot(res_data=None, term=None, rnk=None):
    """
    Create a GSEA enrichment plot from gseapy prerank results.
    If res_data is None, automatically simulates synthetic GSEA result using sim_gsea_data().
    """
    if res_data is None or term is None:
        res_data, term, rnk = sim_gsea_data()

    if hasattr(res_data, "results"):
        res_data = res_data.results

    hits = res_data[term]["hits"]
    resdata = pd.DataFrame({
        "res": res_data[term]["RES"],
        "index": range(len(res_data[term]["RES"]))
    })
    matched_genes = res_data[term]["matched_genes"].split(";")
    nes = round(res_data[term]["nes"], 4)
    pval = round(res_data[term]["pval"], 4)
    fdr = round(res_data[term]["fdr"], 4)

    hits_data = pd.DataFrame({
        "hits": hits,
        "gene": matched_genes
    })
    if rnk is not None:
        hits_data = hits_data.merge(rnk, how="left", on="gene")

    x_position = 0.75 * max(resdata["index"])
    if nes > 0:
        y_position = 0.75 * max(resdata["res"])
    else:
        y_position = -0.05

    point_tooltips = layer_tooltips().title('@gene')
    if rnk is not None and "score" in hits_data.columns:
        point_tooltips = point_tooltips.line('Log2FC|@score')

    p1 = (ggplot(resdata, aes(x='index', y='res')) +
          geom_line(color="green", show_legend=False, tooltips='none') +
          geom_hline(yintercept=0, color="grey", size=0.5, linetype="dashed") +
          geom_point(data=hits_data,
                     mapping=aes(x='hits', y=[resdata['res'][i] for i in hits_data['hits']]),
                     color="red", size=1.5,
                     tooltips=point_tooltips) +
          geom_text(x=x_position, y=y_position,
                    label=f"nes:{nes}\npval:{pval}\nfdr:{fdr}",
                    size=10, hjust=0, vjust=1, fontface="italic", lineheight=1.3) +
          theme_bw() +
          theme(axis_text_x=element_blank(),
                legend_position="none",
                axis_ticks=element_blank(),
                panel_grid_major=element_blank()) +
          _xlab('') + _ylab('Running Enrichment Score ') +
          ggtitle(term) +
          scale_x_continuous(expand=(0, 0)) +
          scale_y_continuous(expand=(0, 0)))

    gsdata = pd.DataFrame({
        "position": [0] * len(resdata),
    })
    gsdata["Description"] = term
    gsdata.loc[hits, "position"] = 1
    heatmap_data = compute_heat_blocks(gsdata)

    p2 = (ggplot() +
          geom_rect(aes(xmin="xmin", xmax="xmax", ymin="ymin", ymax="ymax", fill="col"), data=heatmap_data) +
          geom_vline(aes(xintercept="hits"), color='black', data=hits_data) +
          scale_fill_identity() +
          scale_y_continuous(expand=(0, 0)) +
          scale_x_continuous(expand=(0, 0)) +
          theme(legend_position="none",
                axis_text=element_blank(),
                axis_ticks=element_blank(),
                axis_title=element_blank(),
                panel_background=element_blank()) +
          _xlab("Rank in Ordered Dataset"))

    combined = gggrid([p1, p2], ncol=1, align=True, heights=[0.7, 0.1], vspace=-20) + ggsize(700, 500)
    return combined

visGSEA = gsea_plot
gggsea = gsea_plot
gggsea_plot = gsea_plot


def blitzgsea_plot(signature, geneset, library, result=None, center=True):
    """Create a GSEA enrichment plot from blitzgsea results using lets-plot."""
    try:
        import blitzgsea as blitz
    except ImportError:
        raise ImportError(
            "blitzgsea is required to use blitzgsea_plot. "
            "Please install it with `pip install blitzgsea`."
        )

    if geneset not in library:
        raise KeyError(f"Gene set '{geneset}' not found in library.")

    sig = signature.copy()
    sig.columns = ["gene", "score"]
    sig = sig.sort_values("score", ascending=False).set_index("gene")
    sig = sig[~sig.index.duplicated(keep="first")]

    if center:
        sig["score"] = sig["score"] - sig["score"].mean()

    signature_map = {gene: idx for idx, gene in enumerate(sig.index)}
    gs = set(library[geneset]) & set(sig.index)

    if not gs:
        raise ValueError(f"No genes in gene set '{geneset}' overlap with the signature.")

    running_sum, es = blitz.enrichment_score(
        np.array(np.abs(sig["score"])),
        signature_map,
        gs
    )
    running_sum = list(running_sum)

    hits = [i for i, gene in enumerate(sig.index) if gene in gs]
    matched_genes = ";".join([sig.index[i] for i in hits])

    nes = 0.0
    pval = 0.0
    fdr = 0.0
    if result is not None:
        if geneset in result.index:
            stats = result.loc[geneset]
            nes = stats.get("nes", 0.0)
            pval = stats.get("pval", 0.0)
            fdr = stats.get("fdr", 0.0)

    res_data = {
        geneset: {
            "RES": running_sum,
            "hits": hits,
            "matched_genes": matched_genes,
            "nes": nes,
            "pval": pval,
            "fdr": fdr
        }
    }

    rnk = pd.DataFrame({
        "gene": sig.index.values,
        "score": sig["score"].values
    })

    return gsea_plot(res_data, geneset, rnk=rnk)

visBlitzGSEA = blitzgsea_plot
ggblitzgsea = blitzgsea_plot


# ==============================================================================
# GSEA / ORA Enrichment Lollipop & Concept Network Visualization
# ==============================================================================

def sim_enrichment_data(n_terms=9, seed=42):
    """
    Simulate synthetic pathway enrichment dataset (GO/KEGG/Reactome) for lollipop & network charts.
    Returns DataFrame with columns: Term, Count, p.adjust, RichFactor, Genes, Log2FC.
    """
    np.random.seed(seed)
    pathways = [
        'Cell Cycle (KEGG)', 'p53 Signaling Pathway', 'DNA Replication',
        'Apoptosis Pathway', 'Necroptosis Pathway', 'Autophagy - animal',
        'MAPK Signaling Pathway', 'PI3K-Akt Signaling', 'Ras Signaling Pathway',
        'NF-kappa B Signaling', 'Toll-like Receptor', 'FoxO Signaling Pathway'
    ]
    terms = pathways[:min(n_terms, len(pathways))]
    
    counts = np.random.randint(12, 45, size=len(terms))
    pvals = 10 ** (-np.random.uniform(1.8, 6.5, size=len(terms)))
    rich_factors = counts / np.random.randint(60, 150, size=len(terms))
    
    gene_pools = {
        0: [f'Cycle_G{j:02d}' for j in range(1, 10)],
        1: [f'Death_G{j:02d}' for j in range(1, 10)],
        2: [f'Signal_G{j:02d}' for j in range(1, 10)],
        3: [f'Immune_G{j:02d}' for j in range(1, 10)]
    }

    genes_list = []
    for i, term in enumerate(terms):
        c_idx = (i // 3) % len(gene_pools)
        main_genes = list(np.random.choice(gene_pools[c_idx], size=4, replace=False))
        cross_pool = gene_pools[(c_idx + 1) % len(gene_pools)]
        main_genes.append(np.random.choice(cross_pool))
        genes_list.append(";".join(main_genes))

    df = pd.DataFrame({
        'Term': terms,
        'Count': counts,
        'p.adjust': pvals,
        'neg_log10_p': -np.log10(pvals),
        'RichFactor': rich_factors,
        'Genes': genes_list,
        'x_zero': 0.0
    }).sort_values(by='RichFactor', ascending=True).reset_index(drop=True)
    
    df['Term'] = pd.Categorical(df['Term'], categories=df['Term'].tolist(), ordered=True)
    return df


def visEnrichLollipop(
    data=None,
    top_n=10,
    x='RichFactor',
    color_by='p.adjust',
    size_by='Count',
    palette='pubr',
    title='Enrichment Analysis Lollipop Chart',
    xlab=None,
    ylab='Pathway Terms',
    **kwargs
):
    """
    Visualize GSEA / ORA enrichment results using a Lollipop chart (棒棒糖图).
    If data is None, automatically generates synthetic enrichment data using sim_enrichment_data().
    """
    if data is None:
        df = sim_enrichment_data(n_terms=top_n)
    else:
        df = data.copy()
        if 'x_zero' not in df.columns:
            df['x_zero'] = 0.0
        if color_by == 'p.adjust' and 'neg_log10_p' not in df.columns and 'p.adjust' in df.columns:
            df['neg_log10_p'] = -np.log10(df['p.adjust'].replace(0, 1e-10))
        if top_n and len(df) > top_n:
            df = df.head(top_n)
        df = df.sort_values(by=x, ascending=True).reset_index(drop=True)
        if 'Term' in df.columns:
            df['Term'] = pd.Categorical(df['Term'], categories=df['Term'].tolist(), ordered=True)

    c_col = 'neg_log10_p' if 'neg_log10_p' in df.columns else color_by

    p = (
        _ggplot(df) +
        geom_segment(aes(x='x_zero', xend=x, y='Term', yend='Term'), color='gray70', size=1.2) +
        geom_point(aes(x=x, y='Term', size=size_by, color=c_col)) +
        scale_color_gradient(low='#3C5488', high='#E64B35', name='-log10(p.adj)' if c_col == 'neg_log10_p' else c_col) +
        scale_size(range=[5, 11], name='Gene Count' if size_by == 'Count' else size_by) +
        theme_pubr() +
        ggtitle(title)
    )
    if xlab:
        p += _xlab(xlab)
    else:
        p += _xlab(x)
    if ylab:
        p += _ylab(ylab)

    return p

ggenrich_lollipop = visEnrichLollipop
gglollipop_enrich = visEnrichLollipop


def _add_concentric_legend(p_net, x_pos, y_pos, min_val, mid_val, max_val, title='Gene Count'):
    # Bottom tangent circles: shift mid and min centers slightly downwards
    c_max = pd.DataFrame([{'x': x_pos, 'y': y_pos}])
    c_mid = pd.DataFrame([{'x': x_pos, 'y': y_pos - 0.025}])
    c_min = pd.DataFrame([{'x': x_pos, 'y': y_pos - 0.05}])
    
    y_top_max = y_pos + 0.30
    y_top_mid = y_pos + 0.16
    y_top_min = y_pos + 0.03
    
    lines_df = pd.DataFrame([
        {'x': x_pos, 'y': y_top_max, 'xend': x_pos + 1.2, 'yend': y_top_max, 'label': str(int(max_val))},
        {'x': x_pos, 'y': y_top_mid, 'xend': x_pos + 1.2, 'yend': y_top_mid, 'label': str(int(mid_val))},
        {'x': x_pos, 'y': y_top_min, 'xend': x_pos + 1.2, 'yend': y_top_min, 'label': str(int(min_val))}
    ])
    
    title_df = pd.DataFrame([{'x': x_pos - 0.2, 'y': y_top_max + 0.35, 'label': title}])
    
    p_net += geom_point(data=c_max, mapping=aes('x', 'y'), shape=21, color='gray40', fill='#00000000', size=22.0)
    p_net += geom_point(data=c_mid, mapping=aes('x', 'y'), shape=21, color='gray40', fill='#00000000', size=16.0)
    p_net += geom_point(data=c_min, mapping=aes('x', 'y'), shape=21, color='gray40', fill='#00000000', size=10.0)
    
    p_net += geom_segment(data=lines_df, mapping=aes('x', 'y', xend='xend', yend='yend'), color='gray50', linetype='dashed', size=0.5)
    p_net += geom_text(data=lines_df, mapping=aes(x='xend', y='yend', label='label'), hjust=0, size=7.5, color='black')
    p_net += geom_text(data=title_df, mapping=aes('x', 'y', label='label'), hjust=0, size=8.5, fontface='bold')
    return p_net


def visEnrichNetwork(
    data=None,
    top_n=9,
    genes_per_term=4,
    cluster_pathways=True,
    n_clusters=3,
    show_hulls=True,
    pathway_size_by='Count',
    nested_legend=True,
    cluster_palette='npg',
    palette='bwr',
    title='Clustered Pathway Enrichment Concept Network (cnetplot)',
    **kwargs
):
    """
    Visualize Pathway-Gene Concept Network (cnetplot / network图) with pathway clustering analysis.
    Pathway circle node sizes scale dynamically based on enriched hit gene count ('Count') or RichFactor / percentage ('RichFactor').
    Supports nested concentric circles legend (同心圆重叠图例) when nested_legend=True.
    """
    if data is None:
        df_enrich = sim_enrichment_data(n_terms=top_n)
    else:
        df_enrich = data.head(top_n).copy()

    pathways = df_enrich['Term'].tolist()[:top_n]
    n_terms = len(pathways)
    np.random.seed(42)

    # Build gene hits mapping for each pathway
    term_genes = {}
    for p_name in pathways:
        p_row = df_enrich[df_enrich['Term'] == p_name].iloc[0] if 'Term' in df_enrich.columns else None
        if p_row is not None and 'Genes' in p_row and pd.notna(p_row['Genes']):
            genes = set(str(p_row['Genes']).split(';'))
        else:
            genes = set([f'{p_name[:3]}_Gene_{j+1:02d}' for j in range(genes_per_term)])
        term_genes[p_name] = genes

    # Calculate proportional node sizes for pathways based on Count or RichFactor
    pathway_vals = []
    for p_name in pathways:
        p_row = df_enrich[df_enrich['Term'] == p_name].iloc[0] if 'Term' in df_enrich.columns else None
        if pathway_size_by == 'RichFactor' and p_row is not None and 'RichFactor' in p_row:
            v = float(p_row['RichFactor'])
        elif p_row is not None and 'Count' in p_row:
            v = float(p_row['Count'])
        else:
            v = float(len(term_genes[p_name]))
        pathway_vals.append(v)

    min_v, max_v = min(pathway_vals), max(pathway_vals)
    span = max_v - min_v if max_v > min_v else 1.0
    pathway_sizes = {
        p_name: 10.0 + 12.0 * ((val - min_v) / span)
        for p_name, val in zip(pathways, pathway_vals)
    }

    # Clustering analysis if enabled
    if cluster_pathways and n_terms >= 3:
        n_clusters = min(n_clusters, n_terms // 2 if n_terms >= 4 else 2)
        dist_mat = np.zeros((n_terms, n_terms))
        for i in range(n_terms):
            for j in range(n_terms):
                if i != j:
                    g1, g2 = term_genes[pathways[i]], term_genes[pathways[j]]
                    jaccard = len(g1 & g2) / max(1, len(g1 | g2))
                    dist_mat[i, j] = 1.0 - jaccard

        Z = _linkage(_squareform(dist_mat), method='ward')
        cluster_labels = _fcluster(Z, t=n_clusters, criterion='maxclust')
    else:
        n_clusters = 1
        cluster_labels = np.ones(n_terms, dtype=int)

    # Layout coordinates
    cluster_centers = {}
    c_angles = np.linspace(0, 2*np.pi, n_clusters, endpoint=False)
    r_cluster = 6.0 if n_clusters > 1 else 0.0

    for c_id in range(1, n_clusters + 1):
        cluster_centers[c_id] = (r_cluster * np.cos(c_angles[c_id - 1]), r_cluster * np.sin(c_angles[c_id - 1]))

    nodes = []
    edges = []

    # Map pathways per cluster for angular distribution
    cluster_term_counts = {}
    cluster_term_idx = {}
    for c_id in range(1, n_clusters + 1):
        c_terms = [pathways[k] for k in range(n_terms) if cluster_labels[k] == c_id]
        cluster_term_counts[c_id] = len(c_terms)
        cluster_term_idx[c_id] = 0

    for i, p_name in enumerate(pathways):
        c_id = cluster_labels[i]
        cx, cy = cluster_centers[c_id]
        c_total = cluster_term_counts[c_id]
        idx_in_c = cluster_term_idx[c_id]
        cluster_term_idx[c_id] += 1

        if c_total > 1:
            sub_angle = idx_in_c * (2 * np.pi / c_total) + 0.2
            px = cx + 2.5 * np.cos(sub_angle)
            py = cy + 2.5 * np.sin(sub_angle)
        else:
            px, py = cx, cy

        p_row = df_enrich[df_enrich['Term'] == p_name].iloc[0] if 'Term' in df_enrich.columns else None
        p_val = float(p_row['neg_log10_p']) if p_row is not None and 'neg_log10_p' in p_row else np.random.uniform(2.0, 5.0)

        nodes.append({
            'name': p_name,
            'x': px,
            'y': py,
            'node_type': 'Pathway',
            'Cluster': f'Cluster {c_id}',
            'size': pathway_sizes[p_name],
            'color_val': p_val,
            'label': p_name
        })

        g_list = list(term_genes[p_name])
        g_count = len(g_list)
        g_angles = np.linspace(0, 2*np.pi, g_count, endpoint=False)
        r_gene = 2.4

        for j, g_name in enumerate(g_list):
            gx = px + r_gene * np.cos(g_angles[j])
            gy = py + r_gene * np.sin(g_angles[j])

            nodes.append({
                'name': g_name,
                'x': gx,
                'y': gy,
                'node_type': 'Gene',
                'Cluster': f'Cluster {c_id}',
                'size': 6.0,
                'color_val': np.random.uniform(-2.0, 2.0),
                'label': g_name
            })

            edges.append({'x': px, 'y': py, 'xend': gx, 'yend': gy})

    df_nodes = pd.DataFrame(nodes)
    df_edges = pd.DataFrame(edges)

    p_net = _ggplot()

    # Convex hull polygons for cluster background
    if show_hulls and n_clusters > 1:
        hull_rows = []
        for c_id_str, group in df_nodes.groupby('Cluster'):
            points = group[['x', 'y']].values
            if len(points) >= 3:
                try:
                    hull = _ConvexHull(points)
                    hull_points = points[hull.vertices]
                    center = hull_points.mean(axis=0)
                    poly = center + (hull_points - center) * 1.3
                    for pt in poly:
                        hull_rows.append({'x': pt[0], 'y': pt[1], 'Cluster': c_id_str})
                except Exception:
                    pass
        if hull_rows:
            df_hulls = pd.DataFrame(hull_rows)
            p_net += geom_polygon(data=df_hulls, mapping=aes(x='x', y='y', fill='Cluster'), alpha=0.15)
            p_net += scale_fill_pubr(cluster_palette)

    p_net += geom_segment(data=df_edges, mapping=aes(x='x', y='y', xend='xend', yend='yend'), color='gray85', size=0.6)

    if cluster_pathways and n_clusters > 1:
        p_net += geom_point(data=df_nodes[df_nodes['node_type'] == 'Gene'],
                            mapping=aes(x='x', y='y', color='Cluster'), size=5, shape=19)
        p_net += geom_point(data=df_nodes[df_nodes['node_type'] == 'Pathway'],
                            mapping=aes(x='x', y='y', fill='Cluster', size='size'), shape=21, color='black')
        p_net += scale_color_pubr(cluster_palette)
    else:
        p_net += geom_point(data=df_nodes[df_nodes['node_type'] == 'Gene'],
                            mapping=aes(x='x', y='y', fill='color_val'), shape=21, size=6, color='white')
        p_net += geom_point(data=df_nodes[df_nodes['node_type'] == 'Pathway'],
                            mapping=aes(x='x', y='y', fill='color_val', size='size'), shape=21, color='black')
        p_net += scale_fill_gradient2(low='#2166AC', mid='#F7F7F7', high='#B2182B', midpoint=0, name='Log2FC / -log10(p)')

    p_net += geom_text(data=df_nodes, mapping=aes(x='x', y='y', label='label'), size=8, vjust=-1.2, fontface='bold')
    p_net += theme_void()
    p_net += ggtitle(title)

    if nested_legend:
        p_net += guides(size='none')
        min_v_int, max_v_int = int(round(min_v)), int(round(max_v))
        mid_v_int = int(round((min_v + max_v) / 2))
        max_x = df_nodes['x'].max() + 3.2
        min_y = df_nodes['y'].min() - 0.5
        p_net = _add_concentric_legend(p_net, x_pos=max_x, y_pos=min_y,
                                       min_val=min_v_int, mid_val=mid_v_int, max_val=max_v_int,
                                       title='Gene Count' if pathway_size_by == 'Count' else pathway_size_by)

    return p_net

cnetplot = visEnrichNetwork
visCnetplot = visEnrichNetwork
ggenrich_network = visEnrichNetwork
ggcnetplot = visEnrichNetwork


# ==============================================================================
# 1. ggvolcano / visVolcano — Publication-ready Volcano Plot
# ==============================================================================

def sim_volcano_data(n_genes=2000, n_de=150, seed=42):
    """Simulate synthetic differential gene expression dataset for volcano plot demonstration.

    Returns DataFrame with columns: ``gene``, ``log2FC``, ``pvalue``, ``padj``.
    """
    np.random.seed(seed)
    genes = [f"Gene_{i+1:04d}" for i in range(n_genes)]
    log2fc = np.random.normal(0, 0.6, n_genes)
    pvals = 10 ** (-np.random.exponential(1.2, n_genes))
    pvals = np.clip(pvals, 1e-50, 1.0)

    de_indices = np.random.choice(n_genes, size=n_de, replace=False)
    for idx in de_indices[:n_de // 2]:
        log2fc[idx] = np.random.uniform(1.2, 4.5)
        pvals[idx] = 10 ** (-np.random.uniform(2.0, 15.0))
    for idx in de_indices[n_de // 2:]:
        log2fc[idx] = np.random.uniform(-4.5, -1.2)
        pvals[idx] = 10 ** (-np.random.uniform(2.0, 15.0))

    df = pd.DataFrame({
        "gene": genes,
        "log2FC": log2fc,
        "pvalue": pvals,
        "padj": np.clip(pvals * 1.5, 0, 1.0)
    })
    return df


def ggvolcano(data=None, x="log2FC", y="pvalue", label="gene",
              fc_cutoff=1.0, p_cutoff=0.05,
              neg_log10_y=True,
              top_n=10,
              palette="npg",
              colors=None,
              size=2.0, alpha=0.75,
              title="Volcano Plot", xlab="log2(Fold Change)", ylab="-log10(p-value)",
              show_legend=True, ggtheme=None):
    """Create a publication-ready Volcano plot for differential expression analysis.

    Parameters
    ----------
    data : pd.DataFrame, optional
        Differential expression results table. If None, simulated data is used.
    x : str
        Column name for log2 Fold Change.
    y : str
        Column name for p-value or adjusted p-value.
    label : str
        Column name for gene/molecule labels.
    fc_cutoff : float
        Magnitude threshold for log2 Fold Change (default 1.0).
    p_cutoff : float
        Significance threshold for p-value (default 0.05).
    neg_log10_y : bool
        Whether to convert y to -log10(y) if values are in [0, 1] (default True).
    top_n : int
        Number of top significant genes to annotate with labels (default 10).
    palette : str
        Color palette name for categories (default ``"npg"``).
    colors : dict, optional
        Custom color mapping, e.g. ``{"Up": "#E64B35", "Down": "#3C5488", "NS": "#999999"}``.
    size : float
        Scatter point size.
    alpha : float
        Scatter point opacity.
    title, xlab, ylab : str, optional
        Plot labels.
    show_legend : bool
        Whether to display legend.
    ggtheme : object, optional
        Custom theme.
    """
    if data is None:
        df = sim_volcano_data()
    else:
        df = data.copy()

    if x not in df.columns or y not in df.columns:
        raise ValueError(f"Columns '{x}' or '{y}' not found in data.")

    if label is None or label not in df.columns:
        df['label_col'] = df.index.astype(str)
        label_col = 'label_col'
    else:
        label_col = label

    # Convert y to -log10(y) if needed
    if neg_log10_y and df[y].max() <= 1.0:
        y_trans = -np.log10(df[y].replace(0, 1e-300))
        y_cutoff_trans = -np.log10(p_cutoff)
    else:
        y_trans = df[y]
        y_cutoff_trans = p_cutoff

    df['y_plot'] = y_trans

    # Classify points
    conditions = [
        (df[x] >= fc_cutoff) & (df['y_plot'] >= y_cutoff_trans),
        (df[x] <= -fc_cutoff) & (df['y_plot'] >= y_cutoff_trans)
    ]
    choices = ['Up', 'Down']
    df['Regulation'] = np.select(conditions, choices, default='NS')

    # Color mapping
    color_map = {
        'Up': '#E64B35',
        'Down': '#3C5488',
        'NS': '#999999'
    }
    if colors is not None:
        color_map.update(colors)

    df['color_val'] = df['Regulation'].map(color_map)

    p = ggplot(df, aes(x=x, y='y_plot'))
    p += geom_point(aes(color='color_val'), size=size, alpha=alpha)
    p += scale_color_identity()

    # Cutoff dashed lines
    p += geom_vline(xintercept=fc_cutoff, linetype="dashed", color="gray50", size=0.5)
    p += geom_vline(xintercept=-fc_cutoff, linetype="dashed", color="gray50", size=0.5)
    p += geom_hline(yintercept=y_cutoff_trans, linetype="dashed", color="gray50", size=0.5)

    # Top significant gene labels
    if top_n > 0:
        sig_df = df[df['Regulation'].isin(['Up', 'Down'])].copy()
        if len(sig_df) > 0:
            sig_df['score'] = sig_df['y_plot'] * np.abs(sig_df[x])
            top_genes = sig_df.sort_values('score', ascending=False).head(top_n)
            p += geom_text(data=top_genes,
                           mapping=aes(x=x, y='y_plot', label=label_col),
                           size=8, vjust=-0.7, color='black')

    theme_obj = ggtheme if ggtheme is not None else theme_pubr()
    p += theme_obj
    if title:
        p += ggtitle(title)
    if xlab:
        p += _xlab(xlab)
    if ylab:
        p += _ylab(ylab)

    return p

visVolcano = ggvolcano


# ==============================================================================
# 2. ggraincloud / visRaincloud — Modern Raincloud Plot
# ==============================================================================

def sim_raincloud_data(n_groups=3, n_per_group=60, seed=42):
    """Simulate continuous multimodal dataset for raincloud plot demonstration."""
    np.random.seed(seed)
    groups = [f"Group {chr(65+i)}" for i in range(n_groups)]
    data = []
    for i, g in enumerate(groups):
        mean_val = 10.0 + i * 4.5
        vals = np.concatenate([
            np.random.normal(mean_val, 1.8, n_per_group // 2),
            np.random.normal(mean_val + 2.8, 1.2, n_per_group // 2)
        ])
        for v in vals:
            data.append({"group": g, "value": v})
    return pd.DataFrame(data)


def ggraincloud(data=None, x="group", y="value", fill="group", color="black",
                palette="npg",
                cloud_width=0.35, rain_jitter=0.08, box_width=0.12,
                title="Raincloud Plot", xlab=None, ylab=None,
                show_legend=True, ggtheme=None):
    """Create a modern publication-ready Raincloud plot (Half-violin + Jittered points + Boxplot).

    Parameters
    ----------
    data : pd.DataFrame, optional
        Input data. If None, simulated data is used.
    x : str
        Categorical grouping column.
    y : str
        Continuous numeric column.
    fill : str
        Column name or color for cloud fill.
    color : str
        Color of point borders and boxplots.
    palette : str
        Publication color palette name (default ``"npg"``).
    cloud_width : float
        Width of half-violin density curve (default 0.35).
    rain_jitter : float
        Jitter width for raw scatter points (default 0.08).
    box_width : float
        Width of embedded boxplot (default 0.12).
    title, xlab, ylab : str, optional
        Plot labels.
    show_legend : bool
        Whether to show legend.
    ggtheme : object, optional
        Custom theme.
    """
    if data is None:
        df = sim_raincloud_data()
    else:
        df = data.copy()

    groups = df[x].unique().tolist()
    palette_colors = {
        'npg': ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F', '#8491B4'],
        'nejm': ['#BC3C29', '#0072B5', '#E18727', '#20854E', '#6F99AD', '#FFDC91'],
        'aaas': ['#3B4992', '#EE0000', '#008B45', '#631879', '#008280', '#BB0021'],
        'jco': ['#0073C2', '#EFC000', '#868686', '#CD534C', '#7AA6DC', '#003C67']
    }
    cols = palette_colors.get(palette, palette_colors['npg'])

    # Build Half-Violin Polygons and Jittered Points
    poly_dfs = []
    jitter_rows = []
    np.random.seed(42)

    for idx, g in enumerate(groups):
        sub = df[df[x] == g][y].dropna().values
        if len(sub) < 3:
            continue

        c_hex = cols[idx % len(cols)]
        kde = _gaussian_kde(sub)
        y_grid = np.linspace(sub.min() - 0.5 * sub.std(), sub.max() + 0.5 * sub.std(), 100)
        dens = kde(y_grid)
        dens_scaled = (dens / dens.max()) * cloud_width

        x_pos = idx + 1
        # Half violin on the right side
        poly_x = np.concatenate([[x_pos], x_pos + dens_scaled, [x_pos]])
        poly_y = np.concatenate([[y_grid[0]], y_grid, [y_grid[-1]]])
        poly_df = pd.DataFrame({'x': poly_x, 'y': poly_y, 'group': g, 'col': c_hex})
        poly_dfs.append(poly_df)

        # Jittered rain points on the left side
        j_x = x_pos - 0.18 + np.random.uniform(-rain_jitter, rain_jitter, size=len(sub))
        for jx, vy in zip(j_x, sub):
            jitter_rows.append({'x': jx, 'y': vy, 'group': g, 'col': c_hex})

    all_polys = pd.concat(poly_dfs, ignore_index=True)
    df_jitter = pd.DataFrame(jitter_rows)

    p = ggplot()
    for _, poly in all_polys.groupby('group'):
        p += geom_polygon(data=poly, mapping=aes(x='x', y='y', fill='col'), alpha=0.6, color='gray30', size=0.5)

    p += geom_point(data=df_jitter, mapping=aes(x='x', y='y', color='col'), size=1.8, alpha=0.7)
    p += scale_fill_identity()
    p += scale_color_identity()

    # Mini boxplot in between
    df['x_num'] = df[x].map(lambda g: groups.index(g) + 1 - 0.04)
    p += geom_boxplot(data=df, mapping=aes(x='x_num', y=y), width=box_width, color='black', fill='white', alpha=0.85)

    p += scale_x_continuous(breaks=list(range(1, len(groups) + 1)), labels=groups, expand=[0.1, 0.1])

    theme_obj = ggtheme if ggtheme is not None else theme_pubr()
    p += theme_obj
    if title:
        p += ggtitle(title)
    if xlab:
        p += _xlab(xlab)
    else:
        p += _xlab(x)
    if ylab:
        p += _ylab(ylab)
    else:
        p += _ylab(y)

    return p

visRaincloud = ggraincloud


# ==============================================================================
# 3. ggsurvplot / visSurvival — Kaplan-Meier Survival Plot
# ==============================================================================

def sim_survival_data(n_samples=150, seed=42):
    """Simulate clinical survival dataset with time, event status, and treatment groups."""
    np.random.seed(seed)
    groups = np.random.choice(["Treatment", "Control"], size=n_samples, p=[0.5, 0.5])
    times = []
    status = []
    for g in groups:
        lam = 0.035 if g == "Treatment" else 0.065
        t = np.random.exponential(1.0 / lam)
        censor_time = np.random.uniform(12, 60)
        if t < censor_time:
            times.append(min(60.0, round(t, 1)))
            status.append(1)  # event occurred
        else:
            times.append(min(60.0, round(censor_time, 1)))
            status.append(0)  # censored
    return pd.DataFrame({"time": times, "status": status, "group": groups})


def ggsurvplot(data=None, time="time", status="status", group="group",
               palette="npg", conf_int=True, censored_ticks=True,
               log_rank=True, median_line=True,
               title="Kaplan-Meier Survival Analysis",
               xlab="Time (Months)", ylab="Survival Probability",
               show_legend=True, ggtheme=None):
    """Create a publication-ready Kaplan-Meier survival curve with optional log-rank test and confidence intervals.

    Parameters
    ----------
    data : pd.DataFrame, optional
        Clinical survival dataset. If None, simulated data is used.
    time : str
        Column name for survival time.
    status : str
        Column name for event status (1 = event, 0 = censored).
    group : str, optional
        Column name for grouping / stratification.
    palette : str
        Color palette name (default ``"npg"``).
    conf_int : bool
        Whether to display 95% Greenwood confidence interval ribbons (default True).
    censored_ticks : bool
        Whether to plot tick markers for censored events (default True).
    log_rank : bool
        Whether to compute and annotate Log-rank test p-value (default True).
    median_line : bool
        Whether to plot median survival drop-lines (default True).
    title, xlab, ylab : str, optional
        Plot labels.
    show_legend : bool
        Whether to show legend.
    ggtheme : object, optional
        Custom theme.
    """
    if data is None:
        df = sim_survival_data()
    else:
        df = data.copy()

    if group is None or group not in df.columns:
        df['group_col'] = 'All'
        group_col = 'group_col'
    else:
        group_col = group

    strata = df[group_col].unique().tolist()
    curve_rows = []
    censored_rows = []

    for s in strata:
        sub = df[df[group_col] == s].sort_values(by=time).reset_index(drop=True)
        unique_times = sorted(sub[time].unique())

        n_at_risk = len(sub)
        surv = 1.0
        var_sum = 0.0

        # Starting point at t=0
        curve_rows.append({'time': 0.0, 'surv': 1.0, 'lower': 1.0, 'upper': 1.0, 'group': s})

        for t in unique_times:
            d = len(sub[(sub[time] == t) & (sub[status] == 1)])
            c = len(sub[(sub[time] == t) & (sub[status] == 0)])

            # Censored ticks
            if c > 0 and censored_ticks:
                censored_rows.append({'time': t, 'surv': surv, 'group': s})

            if d > 0:
                if n_at_risk > d:
                    var_sum += d / (n_at_risk * (n_at_risk - d))
                surv = surv * (1.0 - d / n_at_risk)
                se = surv * np.sqrt(var_sum)
                lower = max(0.0, surv - 1.96 * se)
                upper = min(1.0, surv + 1.96 * se)

                # Step effect
                prev_surv = curve_rows[-1]['surv']
                curve_rows.append({'time': t, 'surv': prev_surv, 'lower': lower, 'upper': upper, 'group': s})
                curve_rows.append({'time': t, 'surv': surv, 'lower': lower, 'upper': upper, 'group': s})

            n_at_risk -= (d + c)

    df_curves = pd.DataFrame(curve_rows)
    df_cens = pd.DataFrame(censored_rows)

    p = ggplot()
    if conf_int:
        p += geom_ribbon(data=df_curves, mapping=aes(x='time', ymin='lower', ymax='upper', fill='group'), alpha=0.18)

    p += geom_line(data=df_curves, mapping=aes(x='time', y='surv', color='group'), size=1.2)

    if len(df_cens) > 0 and censored_ticks:
        p += geom_point(data=df_cens, mapping=aes(x='time', y='surv', color='group'), shape=3, size=3.0)

    p += scale_color_pubr(palette)
    p += scale_fill_pubr(palette)
    p += scale_y_continuous(limits=[0, 1.02], expand=[0, 0])

    # Log-rank test computation
    if log_rank and len(strata) == 2:
        s1, s2 = strata[0], strata[1]
        all_times = sorted(df[time].unique())
        o1, e1, var_tot = 0.0, 0.0, 0.0
        n1 = len(df[df[group_col] == s1])
        n2 = len(df[df[group_col] == s2])

        for t in all_times:
            d_tot = len(df[(df[time] == t) & (df[status] == 1)])
            c_tot = len(df[(df[time] == t) & (df[status] == 0)])
            d1 = len(df[(df[group_col] == s1) & (df[time] == t) & (df[status] == 1)])
            n_tot = n1 + n2

            if n_tot > 1 and d_tot > 0:
                e1_t = d_tot * (n1 / n_tot)
                v_t = (n1 * n2 * d_tot * (n_tot - d_tot)) / (n_tot ** 2 * (n_tot - 1)) if n_tot > 1 else 0
                o1 += d1
                e1 += e1_t
                var_tot += v_t

            n1 -= len(df[(df[group_col] == s1) & (df[time] == t)])
            n2 -= len(df[(df[group_col] == s2) & (df[time] == t)])

        if var_tot > 0:
            chi2_stat = ((o1 - e1) ** 2) / var_tot
            p_val = 1.0 - _chi2.cdf(chi2_stat, df=1)
            p_str = f"Log-rank p = {p_val:.4f}" if p_val >= 0.0001 else "Log-rank p < 0.0001"
            max_t = df_curves['time'].max()
            text_df = pd.DataFrame([{'time': max_t * 0.65, 'surv': 0.85, 'label': p_str}])
            p += geom_text(data=text_df, mapping=aes(x='time', y='surv', label='label'), size=9, fontface='italic')

    theme_obj = ggtheme if ggtheme is not None else theme_pubr()
    if not show_legend:
        theme_obj += theme(legend_position='none')
    p += theme_obj

    if title:
        p += ggtitle(title)
    if xlab:
        p += _xlab(xlab)
    if ylab:
        p += _ylab(ylab)

    return p

visSurvival = ggsurvplot


# ==============================================================================
# 4. ggforest / visForest — Publication-ready Forest Plot
# ==============================================================================

def sim_forest_data(n_studies=8, seed=42):
    """Simulate meta-analysis or hazard ratio dataset for forest plot demonstration."""
    np.random.seed(seed)
    studies = [f"Study {i+1} ({2016+i})" for i in range(n_studies)]
    means = np.round(np.random.uniform(0.65, 1.85, size=n_studies), 2)
    lowers = np.round(means * np.random.uniform(0.65, 0.88, size=n_studies), 2)
    uppers = np.round(means * np.random.uniform(1.15, 1.45, size=n_studies), 2)
    pvals = np.round(10 ** (-np.random.uniform(1.2, 4.0, size=n_studies)), 4)
    weights = np.random.randint(50, 300, size=n_studies)
    return pd.DataFrame({
        "study": studies, "mean": means, "lower": lowers, "upper": uppers,
        "pvalue": pvals, "weight": weights
    })


def ggforest(data=None, study="study", mean="mean", lower="lower", upper="upper",
             pvalue="pvalue", weight=None, ref_line=1.0,
             point_color="#3C5488",
             title="Forest Plot (Meta-Analysis / Hazard Ratios)",
             xlab="Hazard Ratio (95% CI)", ylab="Studies / Variables",
             ggtheme=None):
    """Create a publication-ready Forest Plot with point estimates, 95% CIs, and aligned labels.

    Parameters
    ----------
    data : pd.DataFrame, optional
        Study or variable estimates table. If None, simulated data is used.
    study : str
        Column name for study or variable names.
    mean : str
        Column name for effect size (e.g. HR, OR, RR, mean difference).
    lower : str
        Column name for 95% CI lower bound.
    upper : str
        Column name for 95% CI upper bound.
    pvalue : str, optional
        Column name for p-values.
    weight : str, optional
        Column name for study weights (scales point size).
    ref_line : float
        Vertical null-hypothesis reference line (default 1.0 for ratios, 0.0 for differences).
    point_color : str
        Color of point markers and error bars.
    title, xlab, ylab : str, optional
        Plot labels.
    ggtheme : object, optional
        Custom theme.
    """
    if data is None:
        df = sim_forest_data()
    else:
        df = data.copy()

    df = df.reset_index(drop=True)
    df['y_idx'] = len(df) - np.arange(len(df))

    # Format text label for 95% CI
    df['ci_str'] = df.apply(lambda r: f"{r[mean]:.2f} [{r[lower]:.2f}, {r[upper]:.2f}]", axis=1)
    if pvalue and pvalue in df.columns:
        df['p_str'] = df[pvalue].apply(lambda p: f"p = {p:.4f}" if p >= 0.001 else "p < 0.001")
        df['full_label'] = df['ci_str'] + "  " + df['p_str']
    else:
        df['full_label'] = df['ci_str']

    p = ggplot(df, aes(y='y_idx'))
    p += geom_segment(aes(x=lower, xend=upper, y='y_idx', yend='y_idx'), color=point_color, size=1.0)

    if weight and weight in df.columns:
        p += geom_point(aes(x=mean, y='y_idx', size=weight), shape=15, color=point_color)
    else:
        p += geom_point(aes(x=mean, y='y_idx'), shape=15, size=4.0, color=point_color)

    p += geom_vline(xintercept=ref_line, linetype="dashed", color="gray40", size=0.6)

    # Right side text labels
    max_x = df[upper].max() * 1.12
    p += geom_text(aes(x=max_x, y='y_idx', label='full_label'), hjust=0, size=8.0, color='black')

    p += scale_y_continuous(breaks=df['y_idx'].tolist(), labels=df[study].tolist())

    theme_obj = ggtheme if ggtheme is not None else theme_pubr()
    p += theme_obj
    if title:
        p += ggtitle(title)
    if xlab:
        p += _xlab(xlab)
    if ylab:
        p += _ylab(ylab)

    return p

visForest = ggforest


# ==============================================================================
# 5. ggroc / visROC — ROC & Precision-Recall Curves
# ==============================================================================

def sim_roc_data(n_samples=300, n_models=2, seed=42):
    """Simulate ground truth and model predictions for ROC and PR curves."""
    np.random.seed(seed)
    y_true = np.random.binomial(1, 0.45, size=n_samples)
    data = []
    models = ["Model A (Biomarker)", "Model B (Clinical)"][:n_models]
    for m in models:
        noise = np.random.normal(0, 0.35 if "A" in m else 0.55, size=n_samples)
        scores = 1.0 / (1.0 + np.exp(-(y_true * 2.2 - 1.1 + noise)))
        for yt, s in zip(y_true, scores):
            data.append({"y_true": yt, "y_score": s, "model": m})
    return pd.DataFrame(data)


def ggroc(data=None, y_true="y_true", y_score="y_score", group=None,
          plot_type="roc", palette="npg",
          show_auc=True, mark_optimal=True,
          title=None, xlab=None, ylab=None,
          show_legend=True, ggtheme=None):
    """Create publication-ready ROC and Precision-Recall Curves with automated AUC computation.

    Parameters
    ----------
    data : pd.DataFrame, optional
        Data containing true binary labels and predicted probabilities. If None, simulated data is used.
    y_true : str
        Column name for binary ground truth (0 or 1).
    y_score : str
        Column name for continuous predictions / risk scores.
    group : str, optional
        Column name for comparing multiple models / markers.
    plot_type : str
        ``"roc"`` for Receiver Operating Characteristic, or ``"prc"`` for Precision-Recall.
    palette : str
        Color palette name (default ``"npg"``).
    show_auc : bool
        Whether to calculate and display Area Under the Curve (default True).
    mark_optimal : bool
        Whether to mark optimal threshold point using Youden's J statistic (default True).
    title, xlab, ylab : str, optional
        Plot labels.
    show_legend : bool
        Whether to show legend.
    ggtheme : object, optional
        Custom theme.
    """
    if data is None:
        df = sim_roc_data()
        group_col = "model" if group is None and "model" in df.columns else group
    else:
        df = data.copy()
        group_col = group

    if group_col is None or group_col not in df.columns:
        df['model_group'] = 'Model'
        group_col = 'model_group'

    groups = df[group_col].unique().tolist()
    curve_rows = []
    optimal_rows = []
    auc_texts = []

    for g in groups:
        sub = df[df[group_col] == g].sort_values(by=y_score, ascending=False).reset_index(drop=True)
        y_t = sub[y_true].values
        n_pos = np.sum(y_t == 1)
        n_neg = np.sum(y_t == 0)

        if n_pos == 0 or n_neg == 0:
            continue

        tp = np.cumsum(y_t == 1)
        fp = np.cumsum(y_t == 0)
        tpr = tp / n_pos
        fpr = fp / n_neg
        precision = tp / (tp + fp)
        recall = tpr

        _calc_auc = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
        # Add origin point
        if plot_type == "roc":
            x_vals = np.concatenate([[0.0], fpr])
            y_vals = np.concatenate([[0.0], tpr])
            # Trapezoidal AUC
            auc = _calc_auc(y_vals, x_vals)
            auc_texts.append(f"{g} (AUC = {auc:.3f})")

            # Optimal point (Youden's index: max(TPR - FPR))
            j_scores = tpr - fpr
            opt_idx = np.argmax(j_scores)
            optimal_rows.append({'x': fpr[opt_idx], 'y': tpr[opt_idx], 'group': g})
        else:
            x_vals = np.concatenate([[0.0], recall])
            y_vals = np.concatenate([[1.0], precision])
            auc = _calc_auc(y_vals, x_vals)
            auc_texts.append(f"{g} (AUC = {auc:.3f})")

        for xv, yv in zip(x_vals, y_vals):
            curve_rows.append({'x': xv, 'y': yv, 'group': g})

    df_curves = pd.DataFrame(curve_rows)
    df_opt = pd.DataFrame(optimal_rows)

    p = ggplot(df_curves, aes(x='x', y='y', color='group'))
    p += geom_line(size=1.2)

    if plot_type == "roc":
        p += geom_segment(x=0, y=0, xend=1, yend=1, linetype="dashed", color="gray50", size=0.6)
        if mark_optimal and len(df_opt) > 0:
            p += geom_point(data=df_opt, mapping=aes(x='x', y='y'), shape=21, size=4.0, fill='red', color='black')

    p += scale_color_pubr(palette)

    theme_obj = ggtheme if ggtheme is not None else theme_pubr()
    if not show_legend:
        theme_obj += theme(legend_position='none')
    p += theme_obj

    default_title = "ROC Curve Analysis" if plot_type == "roc" else "Precision-Recall Curve"
    default_xlab = "False Positive Rate (1 - Specificity)" if plot_type == "roc" else "Recall (Sensitivity)"
    default_ylab = "True Positive Rate (Sensitivity)" if plot_type == "roc" else "Precision"

    p += ggtitle(title or (f"{default_title}: {', '.join(auc_texts)}" if show_auc else default_title))
    p += _xlab(xlab or default_xlab)
    p += _ylab(ylab or default_ylab)

    return p

visROC = ggroc


# ==============================================================================
# 6. ggdoseresponse / ggic50 — Sigmoidal 4PL Dose-Response Fitting
# ==============================================================================

def _sigmoidal_4pl(x, bottom, top, log_ic50, hill):
    return bottom + (top - bottom) / (1.0 + 10.0 ** ((log_ic50 - x) * hill))


def sim_doseresponse_data(n_doses=8, n_reps=3, seed=42):
    """Simulate drug concentration-response assay dataset."""
    np.random.seed(seed)
    doses = np.logspace(-9, -4, n_doses)
    data = []
    ic50_true = 1e-6
    for d in doses:
        log_d = np.log10(d)
        log_ic50 = np.log10(ic50_true)
        mean_resp = 5.0 + 90.0 / (1.0 + 10.0 ** (-(log_d - log_ic50)))
        for _ in range(n_reps):
            resp = mean_resp + np.random.normal(0, 3.5)
            data.append({"dose": d, "response": max(0.0, min(100.0, resp)), "drug": "Compound X"})
    return pd.DataFrame(data)


def ggdoseresponse(data=None, dose="dose", response="response", group=None,
                   log_transform=True, palette="npg", show_ic50=True,
                   title="Dose-Response IC50 Curve",
                   xlab="Log10 [Dose] (M)", ylab="Response (%)",
                   show_legend=True, ggtheme=None):
    """Create publication-ready Sigmoidal 4PL Dose-Response Curve with automatic IC50/EC50 parameter fitting.

    Parameters
    ----------
    data : pd.DataFrame, optional
        Assay data containing doses and responses. If None, simulated data is used.
    dose : str
        Column name for drug doses/concentrations.
    response : str
        Column name for measured responses/inhibitions.
    group : str, optional
        Column name for multi-drug comparisons.
    log_transform : bool
        Whether to transform dose to log10(dose) (default True).
    palette : str
        Color palette name (default ``"npg"``).
    show_ic50 : bool
        Whether to annotate calculated IC50 values and drop-lines (default True).
    title, xlab, ylab : str, optional
        Plot labels.
    show_legend : bool
        Whether to show legend.
    ggtheme : object, optional
        Custom theme.
    """
    if data is None:
        df = sim_doseresponse_data()
        group_col = "drug" if group is None and "drug" in df.columns else group
    else:
        df = data.copy()
        group_col = group

    if group_col is None or group_col not in df.columns:
        df['drug_group'] = 'Sample'
        group_col = 'drug_group'

    df['log_dose'] = np.log10(df[dose]) if log_transform else df[dose]

    groups = df[group_col].unique().tolist()
    curve_rows = []
    points_rows = []
    ic50_labels = []

    for g in groups:
        sub = df[df[group_col] == g]
        x_data = sub['log_dose'].values
        y_data = sub[response].values

        # Aggregate mean ± SE per dose
        agg = sub.groupby('log_dose')[response].agg(['mean', 'sem']).reset_index()
        for _, r in agg.iterrows():
            points_rows.append({
                'log_dose': r['log_dose'],
                'mean': r['mean'],
                'ymin': r['mean'] - (r['sem'] if pd.notna(r['sem']) else 0),
                'ymax': r['mean'] + (r['sem'] if pd.notna(r['sem']) else 0),
                'group': g
            })

        # Fit 4PL curve
        try:
            p0 = [y_data.min(), y_data.max(), x_data.mean(), 1.0]
            popt, _ = _curve_fit(_sigmoidal_4pl, x_data, y_data, p0=p0, maxfev=5000)
            x_fit = np.linspace(x_data.min() - 0.2, x_data.max() + 0.2, 100)
            y_fit = _sigmoidal_4pl(x_fit, *popt)
            for xf, yf in zip(x_fit, y_fit):
                curve_rows.append({'log_dose': xf, 'response': yf, 'group': g})

            ic50_val = popt[2]
            ic50_labels.append(f"{g} IC50 = 10^({ic50_val:.2f})")
        except Exception:
            pass

    df_points = pd.DataFrame(points_rows)
    df_curves = pd.DataFrame(curve_rows)

    p = ggplot()
    if len(df_curves) > 0:
        p += geom_line(data=df_curves, mapping=aes(x='log_dose', y='response', color='group'), size=1.2)

    p += geom_errorbar(data=df_points, mapping=aes(x='log_dose', ymin='ymin', ymax='ymax', color='group'), width=0.15)
    p += geom_point(data=df_points, mapping=aes(x='log_dose', y='mean', color='group'), size=3.0)

    p += scale_color_pubr(palette)

    theme_obj = ggtheme if ggtheme is not None else theme_pubr()
    if not show_legend:
        theme_obj += theme(legend_position='none')
    p += theme_obj

    if title:
        p += ggtitle(f"{title} ({', '.join(ic50_labels)})" if (show_ic50 and ic50_labels) else title)
    if xlab:
        p += _xlab(xlab)
    if ylab:
        p += _ylab(ylab)

    return p

ggic50 = ggdoseresponse
visDoseResponse = ggdoseresponse


# ==============================================================================
# 7. ggwaterfall / visWaterfall — RECIST Tumor Response Waterfall Plot
# ==============================================================================

def sim_waterfall_data(n_patients=40, seed=42):
    """Simulate oncology clinical trial tumor burden change dataset."""
    np.random.seed(seed)
    changes = np.sort(np.random.uniform(-100, 60, size=n_patients))[::-1]
    groups = []
    for c in changes:
        if c <= -30:
            groups.append("PR / Partial Response")
        elif c >= 20:
            groups.append("PD / Progressive Disease")
        else:
            groups.append("SD / Stable Disease")
    return pd.DataFrame({
        "patient": [f"Pt_{i+1:02d}" for i in range(n_patients)],
        "change": changes,
        "response": groups
    })


def ggwaterfall(data=None, x="patient", y="change", group="response",
                order="desc", pr_cutoff=-30.0, pd_cutoff=20.0,
                palette="npg",
                title="RECIST Tumor Burden Waterfall Plot",
                xlab="Patients", ylab="Maximum Tumor Change from Baseline (%)",
                show_legend=True, ggtheme=None):
    """Create a publication-ready Oncology RECIST Waterfall plot with response cutoff thresholds.

    Parameters
    ----------
    data : pd.DataFrame, optional
        Patient response table. If None, simulated data is used.
    x : str
        Column name for patient / sample IDs.
    y : str
        Column name for percentage change from baseline.
    group : str, optional
        Column name for response categorization or mutation group.
    order : str
        Sorting order: ``"desc"`` or ``"asc"`` (default ``"desc"``).
    pr_cutoff : float
        Partial response percentage threshold (default -30.0%).
    pd_cutoff : float
        Progressive disease percentage threshold (default +20.0%).
    palette : str
        Color palette name (default ``"npg"``).
    title, xlab, ylab : str, optional
        Plot labels.
    show_legend : bool
        Whether to show legend.
    ggtheme : object, optional
        Custom theme.
    """
    if data is None:
        df = sim_waterfall_data()
    else:
        df = data.copy()

    ascending = (order == "asc")
    df = df.sort_values(by=y, ascending=ascending).reset_index(drop=True)
    df['patient_order'] = pd.Categorical(df[x], categories=df[x].tolist(), ordered=True)

    p = ggplot(df, aes(x='patient_order', y=y))
    if group and group in df.columns:
        p += geom_bar(aes(fill=group), stat='identity', width=0.8)
        p += scale_fill_pubr(palette)
    else:
        p += geom_bar(stat='identity', fill='#3C5488', width=0.8)

    p += geom_hline(yintercept=0, color='black', size=0.6)
    if pr_cutoff is not None:
        p += geom_hline(yintercept=pr_cutoff, linetype="dashed", color="#00A087", size=0.6)
    if pd_cutoff is not None:
        p += geom_hline(yintercept=pd_cutoff, linetype="dashed", color="#E64B35", size=0.6)

    theme_obj = ggtheme if ggtheme is not None else theme_pubr()
    theme_obj += theme(axis_text_x=element_blank(), axis_ticks_x=element_blank())
    if not show_legend:
        theme_obj += theme(legend_position='none')
    p += theme_obj

    if title:
        p += ggtitle(title)
    if xlab:
        p += _xlab(xlab)
    if ylab:
        p += _ylab(ylab)

    return p

visWaterfall = ggwaterfall


# ==============================================================================
# 8. ggmanhattan / visManhattan — GWAS Manhattan Plot
# ==============================================================================

def sim_gwas_data(n_snps=2000, n_chrs=8, seed=42):
    """Simulate genome-wide association study dataset for Manhattan plot demonstration."""
    np.random.seed(seed)
    chrs = []
    bps = []
    pvals = []
    snps = []
    snps_per_chr = n_snps // n_chrs
    for c in range(1, n_chrs + 1):
        for s in range(snps_per_chr):
            chrs.append(c)
            bps.append((s + 1) * 25000 + np.random.randint(0, 10000))
            if c in (2, 6) and s in (25, 26, 27, 80, 81):
                p = 10 ** (-np.random.uniform(7.5, 14.0))
            else:
                p = np.random.uniform(1e-5, 1.0)
            pvals.append(p)
            snps.append(f"rs{c*100000 + s:07d}")
    return pd.DataFrame({"chr": chrs, "bp": bps, "pvalue": pvals, "snp": snps})


def ggmanhattan(data=None, chr="chr", bp="bp", p="pvalue", snp="snp",
                suggestive_line=1e-5, genomewide_line=5e-8,
                top_snps=5, colors=None,
                title="GWAS Manhattan Plot", xlab="Chromosome", ylab="-log10(p-value)",
                show_legend=False, ggtheme=None):
    """Create a publication-ready GWAS Manhattan Plot with chromosome block coloring and threshold lines.

    Parameters
    ----------
    data : pd.DataFrame, optional
        GWAS results table. If None, simulated data is used.
    chr : str
        Column name for chromosome identifiers.
    bp : str
        Column name for base-pair positions.
    p : str
        Column name for p-values.
    snp : str, optional
        Column name for SNP identifiers.
    suggestive_line : float
        Suggestive significance threshold (default 1e-5).
    genomewide_line : float
        Genome-wide significance threshold (default 5e-8).
    top_snps : int
        Number of top significant SNPs to annotate (default 5).
    colors : list, optional
        Alternating chromosome colors, e.g. ``["#3C5488", "#4DBBD5"]``.
    title, xlab, ylab : str, optional
        Plot labels.
    show_legend : bool
        Whether to show legend.
    ggtheme : object, optional
        Custom theme.
    """
    if data is None:
        df = sim_gwas_data()
    else:
        df = data.copy()

    df['neg_log10_p'] = -np.log10(df[p].replace(0, 1e-300))

    # Calculate cumulative coordinates
    chr_list = sorted(df[chr].unique())
    cum_bp = 0
    chr_offsets = {}
    chr_centers = {}
    alt_colors = colors or ["#3C5488", "#4DBBD5"]

    for idx, c in enumerate(chr_list):
        sub = df[df[chr] == c]
        min_b, max_b = sub[bp].min(), sub[bp].max()
        chr_offsets[c] = cum_bp - min_b
        chr_centers[c] = cum_bp + (max_b - min_b) / 2
        cum_bp += (max_b - min_b) + 100000

    df['cum_pos'] = df.apply(lambda r: r[bp] + chr_offsets[r[chr]], axis=1)
    df['chr_color'] = df[chr].apply(lambda c: alt_colors[chr_list.index(c) % len(alt_colors)])

    p_plot = ggplot(df, aes(x='cum_pos', y='neg_log10_p'))
    p_plot += geom_point(aes(color='chr_color'), size=1.8, alpha=0.8)
    p_plot += scale_color_identity()

    # Threshold lines
    if suggestive_line:
        p_plot += geom_hline(yintercept=-np.log10(suggestive_line), linetype="dashed", color="blue", size=0.5)
    if genomewide_line:
        p_plot += geom_hline(yintercept=-np.log10(genomewide_line), linetype="dashed", color="red", size=0.5)

    # Annotate top SNPs
    if top_snps > 0 and snp and snp in df.columns:
        top_df = df.sort_values('neg_log10_p', ascending=False).head(top_snps)
        p_plot += geom_text(data=top_df, mapping=aes(x='cum_pos', y='neg_log10_p', label=snp),
                            size=7.5, vjust=-0.8, color='black')

    center_breaks = [chr_centers[c] for c in chr_list]
    center_labels = [str(c) for c in chr_list]
    p_plot += scale_x_continuous(breaks=center_breaks, labels=center_labels, expand=[0.02, 0.02])

    theme_obj = ggtheme if ggtheme is not None else theme_pubr()
    p_plot += theme_obj

    if title:
        p_plot += ggtitle(title)
    if xlab:
        p_plot += _xlab(xlab)
    if ylab:
        p_plot += _ylab(ylab)

    return p_plot

visManhattan = ggmanhattan


# ==============================================================================
# 9. ggblandaltman / visBlandAltman — Bland-Altman Agreement Plot
# ==============================================================================

def sim_blandaltman_data(n_samples=100, seed=42):
    """Simulate method comparison measurement dataset."""
    np.random.seed(seed)
    true_vals = np.random.uniform(50, 150, size=n_samples)
    m1 = true_vals + np.random.normal(0, 4.0, size=n_samples)
    m2 = true_vals + np.random.normal(1.8, 4.2, size=n_samples)
    return pd.DataFrame({"Method_A": m1, "Method_B": m2})


def ggblandaltman(data=None, x="Method_A", y="Method_B",
                  percent_diff=False,
                  point_color="#3C5488", point_size=2.5,
                  title="Bland-Altman Method Agreement Plot",
                  xlab="Mean of Two Methods", ylab="Difference (Method A - Method B)",
                  ggtheme=None):
    """Create a publication-ready Bland-Altman Agreement Plot with Mean Bias and 95% Limits of Agreement.

    Parameters
    ----------
    data : pd.DataFrame, optional
        Measurements from two methods. If None, simulated data is used.
    x : str
        Column name for Method A measurements.
    y : str
        Column name for Method B measurements.
    percent_diff : bool
        Whether to calculate percentage difference (default False).
    point_color : str
        Color of scatter points.
    point_size : float
        Size of scatter points.
    title, xlab, ylab : str, optional
        Plot labels.
    ggtheme : object, optional
        Custom theme.
    """
    if data is None:
        df = sim_blandaltman_data()
    else:
        df = data.copy()

    mean_val = (df[x] + df[y]) / 2.0
    if percent_diff:
        diff_val = (df[x] - df[y]) / mean_val * 100.0
    else:
        diff_val = df[x] - df[y]

    df_plot = pd.DataFrame({'Mean': mean_val, 'Diff': diff_val})
    bias = diff_val.mean()
    sd = diff_val.std()
    upper_loa = bias + 1.96 * sd
    lower_loa = bias - 1.96 * sd

    p = ggplot(df_plot, aes(x='Mean', y='Diff'))
    p += geom_point(color=point_color, size=point_size, alpha=0.7)

    # Bias and LOA lines
    p += geom_hline(yintercept=bias, color="#3C5488", size=0.8)
    p += geom_hline(yintercept=upper_loa, linetype="dashed", color="#E64B35", size=0.7)
    p += geom_hline(yintercept=lower_loa, linetype="dashed", color="#E64B35", size=0.7)

    # Annotations
    max_x = df_plot['Mean'].max() * 0.95
    p += geom_text(x=max_x, y=bias, label=f"Mean Bias: {bias:.2f}", vjust=-0.5, size=8.0, color="#3C5488")
    p += geom_text(x=max_x, y=upper_loa, label=f"+1.96 SD: {upper_loa:.2f}", vjust=-0.5, size=8.0, color="#E64B35")
    p += geom_text(x=max_x, y=lower_loa, label=f"-1.96 SD: {lower_loa:.2f}", vjust=1.3, size=8.0, color="#E64B35")

    theme_obj = ggtheme if ggtheme is not None else theme_pubr()
    p += theme_obj

    if title:
        p += ggtitle(title)
    if xlab:
        p += _xlab(xlab)
    if ylab:
        p += _ylab(ylab)

    return p

visBlandAltman = ggblandaltman


# ==============================================================================
# 10. ggradar / visRadar — Multi-Dimensional Radar / Spider Chart
# ==============================================================================

def sim_radar_data(n_entities=3, n_metrics=6, seed=42):
    """Simulate multi-metric profiling dataset for radar charts."""
    np.random.seed(seed)
    metrics = [f"Metric {chr(65+i)}" for i in range(n_metrics)]
    entities = [f"Profile {i+1}" for i in range(n_entities)]
    rows = []
    for ent in entities:
        row = {"entity": ent}
        for m in metrics:
            row[m] = np.random.uniform(40, 95)
        rows.append(row)
    return pd.DataFrame(rows)


def ggradar(data=None, id="entity", metrics=None,
            max_scale=100.0, palette="npg", alpha=0.25,
            title="Radar / Spider Profile Comparison",
            show_legend=True, ggtheme=None):
    """Create a publication-ready polygonal Radar / Spider Chart for multi-metric comparison.

    Parameters
    ----------
    data : pd.DataFrame, optional
        Wide-format profiling table. If None, simulated data is used.
    id : str
        Column name identifying entities / profiles.
    metrics : list, optional
        List of numeric metric column names to plot.
    max_scale : float
        Maximum scale value (default 100.0).
    palette : str
        Color palette name (default ``"npg"``).
    alpha : float
        Polygon fill transparency (default 0.25).
    title : str, optional
        Plot title.
    show_legend : bool
        Whether to show legend.
    ggtheme : object, optional
        Custom theme.
    """
    if data is None:
        df = sim_radar_data()
        id_col = "entity"
        metric_cols = [c for c in df.columns if c != id_col]
    else:
        df = data.copy()
        id_col = id
        metric_cols = metrics or [c for c in df.columns if c != id_col and pd.api.types.is_numeric_dtype(df[c])]

    k = len(metric_cols)
    if k < 3:
        raise ValueError("Radar chart requires at least 3 metrics.")

    angles = [2 * np.pi * i / k + np.pi / 2 for i in range(k)]

    # 1. Concentric grid polygons (20%, 40%, 60%, 80%, 100%)
    grid_dfs = []
    for level in [0.2, 0.4, 0.6, 0.8, 1.0]:
        gx = [level * np.cos(a) for a in angles] + [level * np.cos(angles[0])]
        gy = [level * np.sin(a) for a in angles] + [level * np.sin(angles[0])]
        grid_dfs.append(pd.DataFrame({'x': gx, 'y': gy, 'level': level}))

    # 2. Spoke lines and axis labels
    spokes = []
    labels = []
    for idx, (a, m) in enumerate(zip(angles, metric_cols)):
        spokes.append({'x': 0.0, 'y': 0.0, 'xend': np.cos(a), 'yend': np.sin(a)})
        labels.append({'x': 1.15 * np.cos(a), 'y': 1.15 * np.sin(a), 'label': m})
    df_spokes = pd.DataFrame(spokes)
    df_labels = pd.DataFrame(labels)

    # 3. Entity Polygons
    poly_rows = []
    entities = df[id_col].unique().tolist()
    for _, row in df.iterrows():
        ent = row[id_col]
        vals = [float(row[m]) / max_scale for m in metric_cols]
        ex = [v * np.cos(a) for v, a in zip(vals, angles)] + [vals[0] * np.cos(angles[0])]
        ey = [v * np.sin(a) for v, a in zip(vals, angles)] + [vals[0] * np.sin(angles[0])]
        for x_val, y_val in zip(ex, ey):
            poly_rows.append({'x': x_val, 'y': y_val, 'entity': ent})
    df_poly = pd.DataFrame(poly_rows)

    p = ggplot()
    for gdf in grid_dfs:
        p += geom_polygon(data=gdf, mapping=aes(x='x', y='y'), fill='#00000000', color='gray80', size=0.4)

    p += geom_segment(data=df_spokes, mapping=aes(x='x', y='y', xend='xend', yend='yend'), color='gray75', size=0.4)
    p += geom_polygon(data=df_poly, mapping=aes(x='x', y='y', fill='entity'), alpha=alpha)
    p += geom_line(data=df_poly, mapping=aes(x='x', y='y', color='entity'), size=1.0)
    p += geom_point(data=df_poly, mapping=aes(x='x', y='y', color='entity'), size=2.5)

    p += geom_text(data=df_labels, mapping=aes(x='x', y='y', label='label'), size=8.0, fontface='bold')

    p += scale_fill_pubr(palette)
    p += scale_color_pubr(palette)
    p += theme_void()

    if title:
        p += ggtitle(title)

    return p

visRadar = ggradar


# ==============================================================================
# 11. ggupset / visUpSet — UpSet Multi-Set Intersection Plot
# ==============================================================================

def sim_upset_data(seed=42):
    """Simulate multi-set binary membership dataset for UpSet plot demonstration."""
    np.random.seed(seed)
    genes = [f"Gene_{i+1:03d}" for i in range(120)]
    sets = ["Set A (Immune)", "Set B (Metabolism)", "Set C (Signaling)", "Set D (Stress)"]
    rows = []
    for g in genes:
        row = {"gene": g}
        for s in sets:
            row[s] = int(np.random.rand() > 0.6)
        rows.append(row)
    return pd.DataFrame(rows)


def ggupset(data=None, sets=None, min_size=1, top_n=12,
            palette="npg", title="UpSet Set Intersections",
            ggtheme=None):
    """Create an UpSet plot for visualizing set intersections and overlaps.

    Parameters
    ----------
    data : pd.DataFrame, optional
        Data containing binary/boolean indicator columns for sets. If None, simulated data is used.
    sets : list, optional
        List of column names representing sets.
    min_size : int
        Minimum intersection count to display (default 1).
    top_n : int
        Maximum number of top intersection combinations to display (default 12).
    palette : str
        Color palette name (default ``"npg"``).
    title : str, optional
        Plot title.
    ggtheme : object, optional
        Custom theme.
    """
    if data is None:
        df = sim_upset_data()
        set_cols = [c for c in df.columns if c != "gene"]
    else:
        df = data.copy()
        set_cols = sets or [c for c in df.columns if df[c].dropna().isin([0, 1, True, False]).all()]

    if len(set_cols) < 2:
        raise ValueError("UpSet plot requires at least 2 binary set columns.")

    # Calculate combination frequencies
    comb_counts = df.groupby(set_cols).size().reset_index(name='count')
    comb_counts = comb_counts[comb_counts[set_cols].sum(axis=1) > 0]
    comb_counts = comb_counts[comb_counts['count'] >= min_size]
    comb_counts = comb_counts.sort_values(by='count', ascending=False).head(top_n).reset_index(drop=True)

    n_combs = len(comb_counts)
    comb_counts['comb_id'] = [f"Comb_{i+1:02d}" for i in range(n_combs)]

    # 1. Top Bar Plot (Intersection Size)
    p_top = (
        ggplot(comb_counts, aes(x='comb_id', y='count')) +
        geom_bar(stat='identity', fill='#3C5488', width=0.65) +
        geom_text(aes(x='comb_id', y='count', label='count'), vjust=-0.5, size=7.5) +
        theme_pubr() +
        theme(axis_text_x=element_blank(), axis_ticks_x=element_blank(), axis_title_x=element_blank()) +
        _ylab("Intersection Size") +
        ggtitle(title)
    )

    # 2. Bottom Dot-Matrix
    matrix_rows = []
    segment_rows = []

    for c_idx, row in comb_counts.iterrows():
        active_y = []
        for s_idx, s_name in enumerate(set_cols):
            val = int(row[s_name])
            matrix_rows.append({
                'comb_id': row['comb_id'],
                'set_name': s_name,
                'x': c_idx + 1,
                'y': s_idx + 1,
                'active': val
            })
            if val == 1:
                active_y.append(s_idx + 1)
        if len(active_y) > 1:
            segment_rows.append({
                'x': c_idx + 1,
                'y': min(active_y),
                'yend': max(active_y)
            })

    df_matrix = pd.DataFrame(matrix_rows)
    df_segments = pd.DataFrame(segment_rows)

    df_active = df_matrix[df_matrix['active'] == 1]
    df_inactive = df_matrix[df_matrix['active'] == 0]

    p_bottom = ggplot()
    if len(df_segments) > 0:
        p_bottom += geom_segment(data=df_segments, mapping=aes(x='x', y='y', xend='x', yend='yend'),
                                 color='gray30', size=1.5)

    p_bottom += geom_point(data=df_inactive, mapping=aes(x='x', y='y'), color='gray80', size=4.5)
    p_bottom += geom_point(data=df_active, mapping=aes(x='x', y='y'), color='#3C5488', size=5.5)

    p_bottom += scale_x_continuous(breaks=list(range(1, n_combs + 1)), labels=comb_counts['comb_id'].tolist(), expand=[0.05, 0.05])
    p_bottom += scale_y_continuous(breaks=list(range(1, len(set_cols) + 1)), labels=set_cols, expand=[0.1, 0.1])
    p_bottom += theme_pubr()
    p_bottom += theme(axis_title_x=element_blank(), axis_title_y=element_blank(),
                      axis_text_x=element_blank(), axis_ticks_x=element_blank())

    combined = gggrid([p_top, p_bottom], ncol=1, heights=[0.6, 0.4], vspace=0)
    return combined

visUpSet = ggupset





