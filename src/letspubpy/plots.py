import numpy as np
import pandas as pd
from scipy import stats as _scipy_stats
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
    scale_y_continuous,
    scale_x_continuous,
    scale_fill_gradient2,
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
