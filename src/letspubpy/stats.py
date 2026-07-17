import re
import numpy as np
import pandas as pd
from scipy import stats
from lets_plot import aes, geom_bracket, geom_text, geom_blank

def clean_mapping_column(val):
    """Extract clean column name from mapping values (like as_discrete('col'))."""
    if not isinstance(val, str):
        return val
    # Handle as_discrete('column', ...)
    match = re.match(r"as_discrete\(['\"](.+?)['\"]", val)
    if match:
        return match.group(1)
    return val

def extract_data_and_mapping(plot):
    """Extract the pandas DataFrame and aesthetic mappings from a PlotSpec object."""
    p_dict = plot.as_dict()
    data = p_dict.get('data')
    mapping = p_dict.get('mapping', {})
    
    # If data is not global, look at the layers
    if data is None or len(data) == 0:
        layers = p_dict.get('layers', [])
        for layer in layers:
            l_data = layer.get('data')
            if l_data is not None and len(l_data) > 0:
                data = l_data
                l_mapping = layer.get('mapping', {})
                mapping = {**mapping, **l_mapping}
                break
                
    return data, mapping

def format_p_value(p, format_type="p.format", hide_ns=False):
    """Format p-value as scientific/decimal format or as significance asterisks."""
    if np.isnan(p):
        return "ns" if not hide_ns else ""
        
    if format_type == "p.signif":
        if p > 0.05:
            return "ns" if not hide_ns else ""
        elif p <= 0.0001:
            return "****"
        elif p <= 0.001:
            return "***"
        elif p <= 0.01:
            return "**"
        else:
            return "*"
    else:
        # Default p.format
        if p < 0.001:
            return f"p = {p:.1e}"
        elif p < 0.01:
            return f"p = {p:.3f}"
        else:
            return f"p = {p:.2f}"

def compute_stats_two_groups(data, x_col, y_col, group1, group2, method="wilcoxon", paired=False):
    """Perform pairwise comparison between two groups in the data."""
    val1 = data[data[x_col] == group1][y_col].values
    val2 = data[data[x_col] == group2][y_col].values
    
    # Remove NaNs
    val1 = val1[~np.isnan(val1)]
    val2 = val2[~np.isnan(val2)]
    
    if len(val1) == 0 or len(val2) == 0:
        return np.nan
        
    method_lower = method.lower()
    if method_lower in ["wilcox.test", "wilcox", "wilcoxon", "mwu", "mannwhitneyu"]:
        if paired:
            if len(val1) != len(val2):
                raise ValueError(f"For paired Wilcoxon test, groups '{group1}' and '{group2}' must be of equal size (got {len(val1)} and {len(val2)}).")
            res = stats.wilcoxon(val1, val2)
        else:
            res = stats.mannwhitneyu(val1, val2, alternative='two-sided')
        return res.pvalue
        
    elif method_lower in ["t.test", "t_test", "ttest"]:
        if paired:
            if len(val1) != len(val2):
                raise ValueError(f"For paired t-test, groups '{group1}' and '{group2}' must be of equal size (got {len(val1)} and {len(val2)}).")
            res = stats.ttest_rel(val1, val2)
        else:
            # Welch's t-test by default (equal_var=False) to match R
            res = stats.ttest_ind(val1, val2, equal_var=False)
        return res.pvalue
    else:
        raise ValueError(f"Unknown pairwise statistical comparison method: {method}")

def compute_stats_global(data, x_col, y_col, method="kruskal.test"):
    """Perform global statistical comparison across all groups."""
    unique_groups = data[x_col].dropna().unique()
    if len(unique_groups) < 2:
        return np.nan, "ns"
        
    groups = []
    for g in unique_groups:
        vals = data[data[x_col] == g][y_col].values
        vals = vals[~np.isnan(vals)]
        if len(vals) > 0:
            groups.append(vals)
            
    if len(groups) < 2:
        return np.nan, "ns"
        
    method_lower = method.lower()
    if method_lower in ["anova", "f_oneway"]:
        res = stats.f_oneway(*groups)
        return res.pvalue, "ANOVA"
    elif method_lower in ["kruskal.test", "kruskal", "kruskal_wallis"]:
        res = stats.kruskal(*groups)
        return res.pvalue, "Kruskal-Wallis"
    else:
        raise ValueError(f"Unknown global statistical comparison method: {method}")

def calculate_bracket_positions(data, y_col, comparisons, label_y=None, step_increase=0.08):
    """Determine the y-coordinates for stacking pairwise significance brackets."""
    y_min = data[y_col].min()
    y_max = data[y_col].max()
    y_range = y_max - y_min if y_max != y_min else 1.0
    
    positions = []
    if label_y is not None:
        if isinstance(label_y, (list, tuple)):
            positions = list(label_y)
        else:
            positions = [label_y] * len(comparisons)
            
    if len(positions) < len(comparisons):
        start_len = len(positions)
        start_y = y_max + 0.05 * y_range if start_len == 0 else positions[-1] + step_increase * y_range
        for i in range(start_len, len(comparisons)):
            pos = start_y + (i - start_len) * step_increase * y_range
            positions.append(pos)
            
    return positions

def make_global_label(data, x_col, y_col, method="kruskal", label_x=None, label_y=None, label="p.format"):
    """Create a geom_text layer displaying global test statistics (ANOVA/Kruskal-Wallis)."""
    p, name = compute_stats_global(data, x_col, y_col, method=method)
    if np.isnan(p):
        return None
        
    p_str = format_p_value(p, format_type=label)
    label_text_str = f"{name}, {p_str}"
    
    y_min = data[y_col].min()
    y_max = data[y_col].max()
    y_range = y_max - y_min if y_max != y_min else 1.0
    
    if label_x is None:
        # Default x coordinate to the first category index (0 in lets-plot)
        label_x = 0.0
    if label_y is None:
        label_y = y_max + 0.02 * y_range
        
    return geom_text(x=label_x, y=label_y, label=label_text_str, hjust=0, vjust=0, size=11)

def add_stat_compare_means(plot, comparisons=None, method="wilcoxon", paired=False,
                           label="p.format", label_x=None, label_y=None,
                           step_increase=0.08, hide_ns=False, **kwargs):
    """Add a statistical comparison layer directly to a PlotSpec object."""
    data, mapping = extract_data_and_mapping(plot)
    if data is None or mapping is None:
        raise ValueError("Could not extract data or mapping from the plot. Make sure the plot has data and aes mappings.")
        
    x_col = clean_mapping_column(mapping.get('x'))
    y_col = clean_mapping_column(mapping.get('y'))
    
    if not x_col or not y_col:
        raise ValueError("Plot is missing required 'x' or 'y' aesthetic mapping.")
        
    if x_col not in data.columns or y_col not in data.columns:
        raise ValueError(f"Aesthetic mapping columns '{x_col}' or '{y_col}' not found in data columns.")
        
    if comparisons is not None:
        # Pairwise comparisons
        p_values = []
        valid_comparisons = []
        for c in comparisons:
            try:
                p = compute_stats_two_groups(data, x_col, y_col, c[0], c[1], method=method, paired=paired)
                if not np.isnan(p):
                    p_values.append(p)
                    valid_comparisons.append(c)
            except Exception as e:
                # Silently ignore comparison errors if a category does not exist
                pass
                
        if not valid_comparisons:
            return plot
            
        positions = calculate_bracket_positions(data, y_col, valid_comparisons, label_y=label_y, step_increase=step_increase)
        
        bracket_df = pd.DataFrame({
            'xmin': [c[0] for c in valid_comparisons],
            'xmax': [c[1] for c in valid_comparisons],
            'y': positions,
            'label': [format_p_value(p, format_type=label, hide_ns=hide_ns) for p in p_values]
        })
        
        # Prepare bracket parameters
        br_params = {}
        if 'color' in kwargs:
            br_params['color'] = kwargs['color']
        if 'size' in kwargs:
            br_params['size'] = kwargs['size']
        if 'segment_color' in kwargs:
            br_params['segment_color'] = kwargs['segment_color']
        if 'segment_size' in kwargs:
            br_params['segment_size'] = kwargs['segment_size']
            
        layer = geom_bracket(aes(xmin='xmin', xmax='xmax', y='y', label='label'), data=bracket_df, **br_params)
        return plot + layer
    else:
        # Global comparison
        global_method = "kruskal.test" if method.lower() in ["wilcoxon", "wilcox", "mwu", "mannwhitneyu", "kruskal", "kruskal.test"] else "anova"
        layer = make_global_label(data, x_col, y_col, method=global_method, label_x=label_x, label_y=label_y, label=label)
        if layer is not None:
            return plot + layer
        return plot

class StatCompareMeansAdder:
    """Helper class to allow adding stat_compare_means to PubPlotSpec using + operator."""
    def __init__(self, comparisons, method, paired, label, label_x, label_y, step_increase, hide_ns, kwargs):
        self.comparisons = comparisons
        self.method = method
        self.paired = paired
        self.label = label
        self.label_x = label_x
        self.label_y = label_y
        self.step_increase = step_increase
        self.hide_ns = hide_ns
        self.kwargs = kwargs
        
    def __radd__(self, plot):
        return add_stat_compare_means(
            plot,
            comparisons=self.comparisons,
            method=self.method,
            paired=self.paired,
            label=self.label,
            label_x=self.label_x,
            label_y=self.label_y,
            step_increase=self.step_increase,
            hide_ns=self.hide_ns,
            **self.kwargs
        )

def stat_compare_means(data=None, x=None, y=None, comparisons=None, method="wilcoxon", paired=False,
                       label="p.format", label_x=None, label_y=None,
                       step_increase=0.08, hide_ns=False, **kwargs):
    """
    Perform statistical tests and add p-values or significance asterisks to the plot.
    
    Can be used:
    1. By adding directly to a letspubpy plot using `+`:
       >>> ggboxplot(df, x="group", y="val") + stat_compare_means(comparisons=[("A", "B")])
    2. As a standalone function returning a geom layer if data, x, and y are provided:
       >>> stat_compare_means(df, x="group", y="val", comparisons=[("A", "B")])
    """
    if data is None:
        return StatCompareMeansAdder(
            comparisons=comparisons,
            method=method,
            paired=paired,
            label=label,
            label_x=label_x,
            label_y=label_y,
            step_increase=step_increase,
            hide_ns=hide_ns,
            kwargs=kwargs
        )
    else:
        # Standalone function usage
        if x is None or y is None:
            raise ValueError("x and y column names must be provided if data is specified.")
            
        x_clean = clean_mapping_column(x)
        y_clean = clean_mapping_column(y)
        
        if comparisons is not None:
            p_values = []
            valid_comparisons = []
            for c in comparisons:
                try:
                    p = compute_stats_two_groups(data, x_clean, y_clean, c[0], c[1], method=method, paired=paired)
                    if not np.isnan(p):
                        p_values.append(p)
                        valid_comparisons.append(c)
                except Exception as e:
                    pass
            if not valid_comparisons:
                return geom_blank()
                
            positions = calculate_bracket_positions(data, y_clean, valid_comparisons, label_y=label_y, step_increase=step_increase)
            
            bracket_df = pd.DataFrame({
                'xmin': [c[0] for c in valid_comparisons],
                'xmax': [c[1] for c in valid_comparisons],
                'y': positions,
                'label': [format_p_value(p, format_type=label, hide_ns=hide_ns) for p in p_values]
            })
            
            br_params = {}
            if 'color' in kwargs:
                br_params['color'] = kwargs['color']
            if 'size' in kwargs:
                br_params['size'] = kwargs['size']
            if 'segment_color' in kwargs:
                br_params['segment_color'] = kwargs['segment_color']
            if 'segment_size' in kwargs:
                br_params['segment_size'] = kwargs['segment_size']
                
            return geom_bracket(aes(xmin='xmin', xmax='xmax', y='y', label='label'), data=bracket_df, **br_params)
        else:
            global_method = "kruskal.test" if method.lower() in ["wilcoxon", "wilcox", "mwu", "mannwhitneyu", "kruskal", "kruskal.test"] else "anova"
            layer = make_global_label(data, x_clean, y_clean, method=global_method, label_x=label_x, label_y=label_y, label=label)
            if layer is not None:
                return layer
            return geom_blank()
