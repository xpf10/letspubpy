import pytest
import numpy as np
import pandas as pd
import letspubpy as lpp
from lets_plot.plot.core import PlotSpec, FeatureSpec
from lets_plot.plot.subplots import SupPlotsSpec

@pytest.fixture
def sample_data():
    np.random.seed(123)
    return pd.DataFrame({
        'group': ['A'] * 10 + ['B'] * 10 + ['C'] * 10,
        'value': np.concatenate([
            np.random.normal(0, 1, 10),
            np.random.normal(1.5, 1, 10),
            np.random.normal(0.5, 1, 10)
        ])
    })

def test_theme_pubr():
    theme = lpp.theme_pubr(base_size=14, base_family="sans", legend="bottom", border=True)
    assert isinstance(theme, FeatureSpec)
    theme_dict = theme.as_dict()
    assert 'feature-list' in theme_dict or theme_dict.get('kind') == 'theme'

def test_ggboxplot(sample_data):
    p = lpp.ggboxplot(sample_data, x='group', y='value', fill='group', palette='npg', add='jitter')
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    assert p_dict['kind'] == 'plot'
    assert len(p_dict['layers']) > 0

def test_ggviolin(sample_data):
    p = lpp.ggviolin(sample_data, x='group', y='value', fill='group', add='boxplot')
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    assert p_dict['kind'] == 'plot'

def test_ggbarplot(sample_data):
    # Testing count
    p_count = lpp.ggbarplot(sample_data, x='group')
    assert isinstance(p_count, lpp.PubPlotSpec)
    
    # Testing mean with error bars
    p_mean = lpp.ggbarplot(sample_data, x='group', y='value', add='mean_se')
    assert isinstance(p_mean, lpp.PubPlotSpec)
    p_dict = p_mean.as_dict()
    # Check that ymin and ymax are mapped in the layers
    errorbar_layer = [l for l in p_dict['layers'] if l.get('geom') == 'errorbar']
    assert len(errorbar_layer) > 0

def test_ggline(sample_data):
    p = lpp.ggline(sample_data, x='group', y='value', add='mean_sd')
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    # Check that geom_line is in the layers
    line_layer = [l for l in p_dict['layers'] if l.get('geom') == 'line']
    assert len(line_layer) > 0

def test_stat_compare_means(sample_data):
    # Standalone test
    bracket = lpp.stat_compare_means(sample_data, x='group', y='value', comparisons=[('A', 'B'), ('B', 'C')])
    assert isinstance(bracket, FeatureSpec)
    
    # Test + addition
    p = lpp.ggboxplot(sample_data, x='group', y='value')
    p2 = p + lpp.stat_compare_means(comparisons=[('A', 'B')])
    p2_dict = p2.as_dict()
    bracket_layers = [l for l in p2_dict['layers'] if l.get('geom') == 'bracket']
    assert len(bracket_layers) > 0
    
    # Global comparison test
    p3 = p + lpp.stat_compare_means(method='anova')
    p3_dict = p3.as_dict()
    text_layers = [l for l in p3_dict['layers'] if l.get('geom') == 'text']
    assert len(text_layers) > 0

def test_ggpie():
    df = pd.DataFrame({
        'name': ['X', 'Y', 'Z'],
        'value': [10, 20, 30]
    })
    p = lpp.ggpie(df, x='value', label='name')
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    pie_layers = [l for l in p_dict['layers'] if l.get('geom') == 'pie']
    assert len(pie_layers) > 0

def test_ggarrange(sample_data):
    p1 = lpp.ggboxplot(sample_data, x='group', y='value')
    p2 = lpp.ggviolin(sample_data, x='group', y='value')
    grid = lpp.ggarrange(p1, p2, ncol=2, common_legend=True)
    assert isinstance(grid, SupPlotsSpec)
    grid_dict = grid.as_dict()
    assert grid_dict['kind'] == 'subplots'
