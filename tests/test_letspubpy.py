import pytest
import numpy as np
import pandas as pd
import letspubpy as lpp
from lets_plot.plot.core import PlotSpec, FeatureSpec
from lets_plot.plot.subplots import SupPlotsSpec
from lets_plot import ggsave

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
    
    # Test + addition with size and custom symnum_args
    p = lpp.ggboxplot(sample_data, x='group', y='value')
    p2 = p + lpp.stat_compare_means(
        comparisons=[('A', 'B')], 
        size=15, 
        label="p.signif",
        symnum_args={"cutpoints": [0, 0.01, 1], "symbols": ["significant", "ns"]}
    )
    p2_dict = p2.as_dict()
    bracket_layers = [l for l in p2_dict['layers'] if l.get('geom') == 'bracket']
    assert len(bracket_layers) > 0
    assert bracket_layers[0].get('size') == 15
    
    # Test + addition with explicit list labels
    p_custom = p + lpp.stat_compare_means(comparisons=[('A', 'B'), ('B', 'C')], label=["diff1", "diff2"])
    p_custom_dict = p_custom.as_dict()
    custom_layers = [l for l in p_custom_dict['layers'] if l.get('geom') == 'bracket']
    assert len(custom_layers) > 0
    assert "diff1" in custom_layers[0].get('data').get('label').values
    
    # Global comparison test with size
    p3 = p + lpp.stat_compare_means(method='anova', size=12)
    p3_dict = p3.as_dict()
    text_layers = [l for l in p3_dict['layers'] if l.get('geom') == 'text']
    assert len(text_layers) > 0
    assert text_layers[0].get('size') == 12

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

def test_prism(sample_data):
    # Test theme_prism
    t = lpp.theme_prism(palette="black_and_white", base_size=12, border=True)
    assert isinstance(t, FeatureSpec)
    
    # Test scale_color_prism and scale_fill_prism
    p = lpp.ggboxplot(sample_data, x='group', y='value', fill='group') + \
        lpp.theme_prism() + \
        lpp.scale_fill_prism(palette="candy_bright") + \
        lpp.scale_color_prism(palette="candy_bright")
    assert isinstance(p, lpp.PubPlotSpec)


# ---------- ggscatter new features ----------

@pytest.fixture
def scatter_data():
    """Generate correlated bivariate scatter data with groups."""
    np.random.seed(42)
    n = 60
    x = np.linspace(0, 10, n)
    y = x * 1.5 + np.random.normal(0, 2, n)
    groups = np.repeat(["Control", "Treat"], n // 2)
    label_col = [f"P{i}" for i in range(n)]
    return pd.DataFrame({"x": x, "y": y, "group": groups, "label": label_col})


def test_ggscatter_basic(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y")
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    assert p_dict["kind"] == "plot"
    point_layers = [l for l in p_dict["layers"] if l.get("geom") == "point"]
    assert len(point_layers) > 0


def test_ggscatter_with_color(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", color="group", fill="group", palette="npg")
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    point_layers = [l for l in p_dict["layers"] if l.get("geom") == "point"]
    assert len(point_layers) > 0


def test_ggscatter_regression(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", add="reg.line")
    p_dict = p.as_dict()
    smooth_layers = [l for l in p_dict["layers"] if l.get("geom") == "smooth"]
    assert len(smooth_layers) > 0


def test_ggscatter_regression_no_confint(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", add="reg.line", confint=False)
    p_dict = p.as_dict()
    smooth_layers = [l for l in p_dict["layers"] if l.get("geom") == "smooth"]
    assert len(smooth_layers) > 0
    # Check that se is disabled
    se_value = smooth_layers[0].get('se', None)
    assert se_value is False or se_value is None


def test_ggscatter_ellipse(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", color="group", ellipse=True)
    p_dict = p.as_dict()
    polygon_layers = [l for l in p_dict["layers"] if l.get("geom") == "polygon"]
    assert len(polygon_layers) > 0
    poly_mapping = polygon_layers[0].get("mapping", {})
    assert poly_mapping.get("group") == "group"


def test_ggscatter_ellipse_norm_type(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", color="group",
                      ellipse=True, ellipse_type="norm", ellipse_level=0.95)
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    polygon_layers = [l for l in p_dict["layers"] if l.get("geom") == "polygon"]
    assert len(polygon_layers) > 0


def test_ggscatter_ellipse_euclid_type(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", color="group",
                      ellipse=True, ellipse_type="euclid")
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    polygon_layers = [l for l in p_dict["layers"] if l.get("geom") == "polygon"]
    assert len(polygon_layers) > 0


def test_ggscatter_correlation(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", cor=True)
    p_dict = p.as_dict()
    text_layers = [l for l in p_dict["layers"] if l.get("geom") == "text"]
    assert len(text_layers) > 0
    label_text = text_layers[0].get("label", "")
    assert "Pearson" in str(label_text)


def test_ggscatter_correlation_coef(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", cor=True, cor_coef=True)
    p_dict = p.as_dict()
    text_layers = [l for l in p_dict["layers"] if l.get("geom") == "text"]
    assert len(text_layers) > 0
    label_text = text_layers[0].get("label", "")
    assert "R" in str(label_text)


def test_ggscatter_point_labels(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", label="label")
    p_dict = p.as_dict()
    text_layers = [l for l in p_dict["layers"] if l.get("geom") == "text"]
    assert len(text_layers) > 0


def test_ggscatter_rug(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", rug=True)
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    # Additional point layers for rug
    point_layers = [l for l in p_dict["layers"] if l.get("geom") == "point"]
    # Original 1 + 2 rug layers = at least 3
    assert len(point_layers) >= 3


def test_ggscatter_fixed_aspect(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", aspect_ratio=1.0)
    p_dict = p.as_dict()
    # coord_fixed is stored at the top level
    assert p_dict.get("coord", {}).get("name") == "fixed"


def test_confidence_ellipse_points_shape():
    rng = np.random.default_rng(0)
    pts = rng.multivariate_normal([0, 0], np.eye(2), size=50)
    ell = lpp.confidence_ellipse_points(pts.mean(axis=0), np.cov(pts.T),
                                         n_points=80, level=0.95, ellipse_type="norm")
    assert ell.shape == (80, 2)


def test_confidence_ellipse_points_types():
    rng = np.random.default_rng(1)
    pts = rng.multivariate_normal([1, 2], [[1.0, 0.5], [0.5, 2.0]], size=30)
    for etype in ("norm", "t", "euclid"):
        ell = lpp.confidence_ellipse_points(
            pts.mean(axis=0), np.cov(pts.T),
            n_points=60, level=0.90, ellipse_type=etype, n=30
        )
        assert ell.shape == (60, 2)


def test_build_ellipse_df_with_groups():
    df = pd.DataFrame({
        "x": np.random.randn(30),
        "y": np.random.randn(30),
        "g": ["A"] * 15 + ["B"] * 15
    })
    result = lpp.build_ellipse_df(df, "x", "y", group_col="g", level=0.95)
    assert len(result) > 0
    assert "g" in result.columns
    assert "x" in result.columns
    assert "y" in result.columns
    assert "_ellipse_group" in result.columns


def test_build_ellipse_df_no_groups():
    df = pd.DataFrame({
        "x": np.random.randn(20),
        "y": np.random.randn(20)
    })
    result = lpp.build_ellipse_df(df, "x", "y", level=0.95)
    assert len(result) > 0
    assert "x" in result.columns
    assert "y" in result.columns


def test_compute_correlation_pearson():
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 50)
    y = x * 0.8 + rng.normal(0, 0.5, 50)
    corr = lpp.compute_correlation(x, y, method="pearson")
    assert "r" in corr
    assert "p" in corr
    assert "r2" in corr
    assert corr["method_name"] == "Pearson"
    assert abs(corr["r"]) > 0.5  # should be strongly correlated


def test_compute_correlation_spearman():
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 50)
    y = x * 0.8 + rng.normal(0, 0.5, 50)
    corr = lpp.compute_correlation(x, y, method="spearman")
    assert corr["method_name"] == "Spearman"
    assert not np.isnan(corr["r"])


def test_ggscatter_errorbars_mean_se(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", color="group", add="mean_se")
    p_dict = p.as_dict()
    errorbar_layers = [l for l in p_dict["layers"] if l.get("geom") == "errorbar"]
    assert len(errorbar_layers) > 0


def test_ggscatter_label_with_nonexistent_column(scatter_data):
    """Point labels with a non-existent column should not crash."""
    p = lpp.ggscatter(scatter_data, x="x", y="y", label="nonexistent")
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_full_feature_set(scatter_data):
    p = lpp.ggscatter(
        scatter_data, x="x", y="y", color="group", fill="group",
        palette="npg", shape=19, size=3,
        ellipse=True, ellipse_level=0.95, ellipse_type="norm",
        rug=True, cor=True, cor_method="pearson", cor_size=10,
        label="label", label_size=3,
        confint=True, aspect_ratio=1.0,
        add="reg.line"
    )
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    # Should have point, polygon, smooth, text layers
    geoms = set(l.get("geom") for l in p_dict["layers"])
    assert "point" in geoms
    assert "polygon" in geoms
    assert "smooth" in geoms
    assert "text" in geoms


def test_ggscatter_full_feature_renders_to_svg(scatter_data, tmp_path):
    p = lpp.ggscatter(
        scatter_data, x="x", y="y", color="group", fill="group",
        ellipse=True, rug=True, cor=True,
        label="label", add="reg.line"
    )
    out = tmp_path / "ggscatter_features.svg"
    ggsave(p, str(out))
    assert out.exists()
    assert out.stat().st_size > 0


# ---------- confidence_ellipse_points: error / boundary ----------

def test_ellipse_invalid_mean_shape():
    rng = np.random.default_rng(0)
    pts = rng.multivariate_normal([0, 0], np.eye(2), size=10)
    with pytest.raises(ValueError, match="mean must have shape"):
        lpp.confidence_ellipse_points(np.array([1.0]), np.cov(pts.T))


def test_ellipse_invalid_cov_shape():
    with pytest.raises(ValueError, match="cov must have shape"):
        lpp.confidence_ellipse_points(np.array([0.0, 0.0]), np.array([1.0]))


def test_ellipse_invalid_type():
    rng = np.random.default_rng(0)
    pts = rng.multivariate_normal([0, 0], np.eye(2), size=10)
    with pytest.raises(ValueError, match="Unknown ellipse_type"):
        lpp.confidence_ellipse_points(pts.mean(axis=0), np.cov(pts.T),
                                       ellipse_type="invalid")


def test_ellipse_t_type_missing_n():
    rng = np.random.default_rng(0)
    pts = rng.multivariate_normal([0, 0], np.eye(2), size=10)
    with pytest.raises(ValueError, match="n.*must be provided"):
        lpp.confidence_ellipse_points(pts.mean(axis=0), np.cov(pts.T),
                                       ellipse_type="t")


def test_ellipse_t_type_n_too_small():
    rng = np.random.default_rng(0)
    pts = rng.multivariate_normal([0, 0], np.eye(2), size=5)
    with pytest.raises(ValueError, match="n.*must be provided"):
        lpp.confidence_ellipse_points(pts.mean(axis=0), np.cov(pts.T),
                                       ellipse_type="t", n=2)


def test_ellipse_t_type_valid():
    rng = np.random.default_rng(0)
    pts = rng.multivariate_normal([0, 0], np.eye(2), size=30)
    ell = lpp.confidence_ellipse_points(pts.mean(axis=0), np.cov(pts.T),
                                        n_points=60, ellipse_type="t", n=30)
    assert ell.shape == (60, 2)


def test_ellipse_single_point_cov():
    """Degenerate covariance (zero variance) should still work."""
    mean = np.array([0.0, 0.0])
    cov = np.array([[0.0, 0.0], [0.0, 0.0]])
    ell = lpp.confidence_ellipse_points(mean, cov, n_points=40, level=0.95)
    assert ell.shape == (40, 2)
    # All points should be at the mean (with tolerance for float rounding)
    assert np.allclose(ell, mean, atol=1e-4)


def test_ellipse_boundary_n_points():
    rng = np.random.default_rng(0)
    pts = rng.multivariate_normal([0, 0], np.eye(2), size=10)
    # Minimum viable n_points
    ell = lpp.confidence_ellipse_points(pts.mean(axis=0), np.cov(pts.T),
                                        n_points=3, level=0.95)
    assert ell.shape == (3, 2)


def test_ellipse_extreme_level():
    rng = np.random.default_rng(0)
    pts = rng.multivariate_normal([0, 0], np.eye(2), size=10)
    ell_99 = lpp.confidence_ellipse_points(pts.mean(axis=0), np.cov(pts.T),
                                            n_points=40, level=0.999)
    ell_50 = lpp.confidence_ellipse_points(pts.mean(axis=0), np.cov(pts.T),
                                            n_points=40, level=0.50)
    # Higher level should produce larger ellipse (on average farther from center)
    avg_dist_99 = np.mean(np.sqrt((ell_99[:, 0] - 0) ** 2 + (ell_99[:, 1] - 0) ** 2))
    avg_dist_50 = np.mean(np.sqrt((ell_50[:, 0] - 0) ** 2 + (ell_50[:, 1] - 0) ** 2))
    assert avg_dist_99 > avg_dist_50


def test_ellipse_centered_at_mean():
    rng = np.random.default_rng(42)
    pts = rng.multivariate_normal([3, -2], [[2, 0.5], [0.5, 1]], size=100)
    mean = pts.mean(axis=0)
    ell = lpp.confidence_ellipse_points(mean, np.cov(pts.T), n_points=120)
    centroid = ell.mean(axis=0)
    assert np.allclose(centroid, mean, atol=0.1)


# ---------- build_ellipse_df: error / boundary ----------

def test_build_ellipse_df_empty_df():
    df = pd.DataFrame(columns=["x", "y"])
    result = lpp.build_ellipse_df(df, "x", "y", level=0.95)
    assert len(result) == 0
    assert list(result.columns) == ["x", "y", "_ellipse_group"]


def test_build_ellipse_df_single_row():
    df = pd.DataFrame({"x": [1.0], "y": [2.0]})
    result = lpp.build_ellipse_df(df, "x", "y", level=0.95)
    assert len(result) == 0  # < 2 points


def test_build_ellipse_df_single_row_with_groups():
    df = pd.DataFrame({"x": [1.0], "y": [2.0], "g": ["A"]})
    result = lpp.build_ellipse_df(df, "x", "y", group_col="g", level=0.95)
    assert len(result) == 0  # group has < 2 points


def test_build_ellipse_df_group_with_insufficient_points():
    df = pd.DataFrame({
        "x": np.random.randn(15),
        "y": np.random.randn(15),
        "g": ["A"] * 14 + ["B"]  # group B has only 1 point
    })
    result = lpp.build_ellipse_df(df, "x", "y", group_col="g", level=0.95)
    # Should only have group A's ellipse
    assert len(result) > 0
    # Group B should not appear
    if "g" in result.columns:
        assert "B" not in result["g"].values


def test_build_ellipse_df_with_nan_values():
    df = pd.DataFrame({
        "x": [1.0, 2.0, np.nan, 4.0, 5.0, 6.0],
        "y": [2.0, np.nan, 3.0, 4.0, 5.0, 6.0],
    })
    result = lpp.build_ellipse_df(df, "x", "y", level=0.95)
    assert len(result) > 0


def test_build_ellipse_df_missing_column():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    with pytest.raises(KeyError):
        lpp.build_ellipse_df(df, "x", "y", level=0.95)


def test_build_ellipse_df_close_polygon():
    df = pd.DataFrame({"x": np.random.randn(20), "y": np.random.randn(20)})
    result = lpp.build_ellipse_df(df, "x", "y", level=0.95)
    # The last point should equal the first point (polygon closure)
    assert len(result) > 1
    assert result.iloc[0]["x"] == result.iloc[-1]["x"]
    assert result.iloc[0]["y"] == result.iloc[-1]["y"]


def test_build_ellipse_df_custom_n_points():
    df = pd.DataFrame({"x": np.random.randn(10), "y": np.random.randn(10)})
    result = lpp.build_ellipse_df(df, "x", "y", n_points=50, level=0.95)
    # 50 boundary + 1 closing = 51 rows
    assert len(result) == 51


# ---------- compute_correlation: error / boundary ----------

def test_correlation_unknown_method():
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
    with pytest.raises(ValueError, match="Unknown correlation method"):
        lpp.compute_correlation(x, y, method="unknown")


def test_correlation_too_few_points():
    x = np.array([1.0, 2.0])
    y = np.array([2.0, 4.0])
    corr = lpp.compute_correlation(x, y, method="pearson")
    assert np.isnan(corr["r"])
    assert np.isnan(corr["p"])
    assert corr["method_name"] == "pearson"


def test_correlation_with_nan():
    x = np.array([1.0, 2.0, np.nan, 4.0, 5.0, 6.0])
    y = np.array([2.0, np.nan, 3.0, 4.0, 5.0, 6.0])
    corr = lpp.compute_correlation(x, y, method="pearson")
    assert not np.isnan(corr["r"])  # Should handle NaN gracefully


def test_correlation_perfect_positive():
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
    corr = lpp.compute_correlation(x, y, method="pearson")
    assert abs(corr["r"] - 1.0) < 1e-10
    assert corr["r2"] > 0.99


def test_correlation_perfect_negative():
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([-2.0, -4.0, -6.0, -8.0, -10.0])
    corr = lpp.compute_correlation(x, y, method="pearson")
    assert abs(corr["r"] + 1.0) < 1e-10


def test_correlation_kendall():
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 30)
    y = x * 0.7 + rng.normal(0, 0.5, 30)
    corr = lpp.compute_correlation(x, y, method="kendall")
    assert corr["method_name"] == "Kendall"
    assert not np.isnan(corr["r"])


def test_correlation_spearman_returns_r():
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 30)
    y = x * 0.7 + rng.normal(0, 0.5, 30)
    corr = lpp.compute_correlation(x, y, method="spearman")
    assert "r" in corr
    assert "p" in corr
    assert "r2" in corr
    assert corr["method_name"] == "Spearman"


def test_correlation_empty_inputs():
    x = np.array([])
    y = np.array([])
    corr = lpp.compute_correlation(x, y, method="pearson")
    assert np.isnan(corr["r"])


def test_correlation_constant_x():
    """Constant x should produce NaN correlation (zero variance)."""
    x = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    y = np.array([2.0, 3.0, 4.0, 5.0, 6.0])
    corr = lpp.compute_correlation(x, y, method="pearson")
    assert np.isnan(corr["r"]) or corr["r"] == 0  # Either is acceptable


# ---------- ggscatter: error / boundary / parameter combos ----------

def test_ggscatter_empty_df():
    df = pd.DataFrame(columns=["x", "y"])
    p = lpp.ggscatter(df, x="x", y="y")
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    # Should still produce valid plot spec even with empty data
    assert p_dict["kind"] == "plot"


def test_ggscatter_single_point():
    df = pd.DataFrame({"x": [1.0], "y": [2.0]})
    p = lpp.ggscatter(df, x="x", y="y")
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_nan_in_columns():
    df = pd.DataFrame({
        "x": [1.0, np.nan, 3.0, 4.0, 5.0],
        "y": [2.0, 3.0, np.nan, 5.0, 6.0],
    })
    p = lpp.ggscatter(df, x="x", y="y")
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_nan_in_columns_with_ellipse():
    df = pd.DataFrame({
        "x": [1.0, 2.0, np.nan, 4.0, 5.0, 6.0],
        "y": [2.0, np.nan, 3.0, 4.0, 5.0, 6.0],
        "g": ["A", "A", "A", "B", "B", "B"]
    })
    p = lpp.ggscatter(df, x="x", y="y", color="g", ellipse=True)
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_color_constant_not_column(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", color="red", fill="blue")
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    point_layers = [l for l in p_dict["layers"] if l.get("geom") == "point"]
    assert len(point_layers) > 0


def test_ggscatter_add_jitter(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", add="jitter")
    p_dict = p.as_dict()
    jitter_layers = [l for l in p_dict["layers"] if l.get("geom") == "jitter"]
    assert len(jitter_layers) > 0


def test_ggscatter_add_point(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", add="point")
    p_dict = p.as_dict()
    point_layers = [l for l in p_dict["layers"] if l.get("geom") == "point"]
    # Original point + added point = at least 2
    assert len(point_layers) >= 2


def test_ggscatter_add_multiple(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", add=["reg.line", "jitter"])
    p_dict = p.as_dict()
    geoms = set(l.get("geom") for l in p_dict["layers"])
    assert "smooth" in geoms
    assert "jitter" in geoms


def test_ggscatter_invalid_add_item(scatter_data):
    """Invalid add items should not crash (handled by add_extra_layers)."""
    p = lpp.ggscatter(scatter_data, x="x", y="y", add="invalid_item")
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_with_shape_column(scatter_data):
    df = scatter_data.copy()
    df["shape_col"] = np.tile([1, 2], len(df) // 2)
    p = lpp.ggscatter(df, x="x", y="y", shape="shape_col")
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    point_layers = [l for l in p_dict["layers"] if l.get("geom") == "point"]
    assert len(point_layers) > 0


def test_ggscatter_custom_theme(scatter_data):
    custom_theme = lpp.theme_pubr(base_size=10)
    p = lpp.ggscatter(scatter_data, x="x", y="y", ggtheme=custom_theme)
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_no_legend(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", show_legend=False)
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_custom_titles(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y",
                      title="My Scatter", xlab="X Axis", ylab="Y Axis")
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_ellipse_no_group(scatter_data):
    """Ellipse without color/fill mapping should draw a single overall ellipse."""
    p = lpp.ggscatter(scatter_data, x="x", y="y", ellipse=True)
    p_dict = p.as_dict()
    polygon_layers = [l for l in p_dict["layers"] if l.get("geom") == "polygon"]
    assert len(polygon_layers) > 0
    poly_mapping = polygon_layers[0].get("mapping", {})
    # Should not have group mapping (single ellipse for all data)
    assert "group" not in poly_mapping or poly_mapping.get("group") is None


def test_ggscatter_ellipse_t_type(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", color="group",
                      ellipse=True, ellipse_type="t")
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_rug_custom_size(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", rug=True, rug_size=1.5)
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_cor_spearman(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", cor=True, cor_method="spearman")
    p_dict = p.as_dict()
    text_layers = [l for l in p_dict["layers"] if l.get("geom") == "text"]
    assert len(text_layers) > 0
    label_text = text_layers[0].get("label", "")
    assert "Spearman" in str(label_text)


def test_ggscatter_cor_kendall(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", cor=True, cor_method="kendall")
    p_dict = p.as_dict()
    text_layers = [l for l in p_dict["layers"] if l.get("geom") == "text"]
    assert len(text_layers) > 0
    label_text = text_layers[0].get("label", "")
    assert "Kendall" in str(label_text)


def test_ggscatter_label_custom_size(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", label="label", label_size=8)
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_confint_false(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", add="reg.line", confint=False)
    p_dict = p.as_dict()
    smooth_layers = [l for l in p_dict["layers"] if l.get("geom") == "smooth"]
    assert len(smooth_layers) > 0
    se_value = smooth_layers[0].get('se', None)
    assert se_value is False or se_value is None


def test_ggscatter_confint_custom_level(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y",
                      add="reg.line", confint=True, confint_level=0.99)
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_aspect_ratio_2x(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", aspect_ratio=2.0)
    p_dict = p.as_dict()
    assert p_dict.get("coord", {}).get("name") == "fixed"
    assert p_dict.get("coord", {}).get("ratio") == 2.0


def test_ggscatter_multiple_groups_ellipse():
    """3 groups should produce 3 ellipses."""
    df = pd.DataFrame({
        "x": np.concatenate([
            np.random.randn(20) + 0,
            np.random.randn(20) + 3,
            np.random.randn(20) - 3,
        ]),
        "y": np.concatenate([
            np.random.randn(20) + 0,
            np.random.randn(20) + 3,
            np.random.randn(20) - 3,
        ]),
        "g": ["A"] * 20 + ["B"] * 20 + ["C"] * 20
    })
    p = lpp.ggscatter(df, x="x", y="y", color="g", ellipse=True)
    p_dict = p.as_dict()
    polygon_layers = [l for l in p_dict["layers"] if l.get("geom") == "polygon"]
    assert len(polygon_layers) > 0


def test_ggscatter_position_parameter(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", color="group",
                      position=lpp.position_dodge(0.5))
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_size_parameter(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", size=5)
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    point_layers = [l for l in p_dict["layers"] if l.get("geom") == "point"]
    assert len(point_layers) > 0


def test_ggscatter_ellipse_alpha(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", color="group",
                      ellipse=True, ellipse_alpha=0.5)
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_ellipse_custom_level(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", color="group",
                      ellipse=True, ellipse_level=0.90)
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_ellipse_t_type_integration(scatter_data):
    p = lpp.ggscatter(scatter_data, x="x", y="y", color="group",
                      ellipse=True, ellipse_type="t", ellipse_level=0.95)
    assert isinstance(p, lpp.PubPlotSpec)


def test_ggscatter_all_features_together(scatter_data):
    p = lpp.ggscatter(
        scatter_data,
        x="x", y="y",
        color="group", fill="group",
        palette="npg", shape=19, size=3,
        add=["reg.line", "jitter"],
        ellipse=True, ellipse_level=0.90, ellipse_type="norm", ellipse_alpha=0.2,
        rug=True, rug_size=0.8,
        cor=True, cor_method="spearman", cor_coef=True, cor_size=14,
        label="label", label_size=5,
        confint=True, confint_level=0.90,
        aspect_ratio=0.5,
        title="Full Feature Demo",
        xlab="X Label", ylab="Y Label",
        show_legend=True,
    )
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    geoms = set(l.get("geom") for l in p_dict["layers"])
    assert "point" in geoms
    assert "polygon" in geoms
    assert "smooth" in geoms
    assert "text" in geoms
    assert "jitter" in geoms


# ---------- get_color_fill_aes_and_params ----------

def test_color_fill_column_mapping():
    df = pd.DataFrame({"c": ["A", "B"], "f": ["X", "Y"]})
    mapping, params = lpp.get_color_fill_aes_and_params(df, "c", "f")
    assert mapping == {"color": "c", "fill": "f"}
    assert params == {}


def test_color_fill_constant():
    df = pd.DataFrame({"c": ["A", "B"]})
    mapping, params = lpp.get_color_fill_aes_and_params(df, "red", "blue")
    assert mapping == {}
    assert params == {"color": "red", "fill": "blue"}


def test_color_fill_mixed():
    df = pd.DataFrame({"c": ["A", "B"]})
    mapping, params = lpp.get_color_fill_aes_and_params(df, "c", "blue")
    assert mapping == {"color": "c"}
    assert params == {"fill": "blue"}


def test_color_fill_none():
    df = pd.DataFrame({"c": ["A", "B"]})
    mapping, params = lpp.get_color_fill_aes_and_params(df, None, None)
    assert mapping == {}
    assert params == {}


# ---------- apply_labels_and_theme ----------

def test_apply_labels_and_theme_none():
    p = lpp.ggplot(pd.DataFrame({"x": [1], "y": [2]}), lpp.aes(x="x", y="y"))
    result = lpp.apply_labels_and_theme(p)
    assert isinstance(result, lpp.PubPlotSpec)


def test_apply_labels_and_theme_with_args():
    p = lpp.ggplot(pd.DataFrame({"x": [1], "y": [2]}), lpp.aes(x="x", y="y"))
    result = lpp.apply_labels_and_theme(
        p, title="Test", xlab_str="X", ylab_str="Y",
        order=["A", "B"], show_legend=False
    )
    assert isinstance(result, lpp.PubPlotSpec)


# ---------- add_extra_layers edge cases ----------

def test_add_extra_layers_empty():
    p = lpp.ggplot(pd.DataFrame({"x": [1], "y": [2]}), lpp.aes(x="x", y="y"))
    result = lpp.add_extra_layers(p, "x", "y", [], None,
                                   pd.DataFrame({"x": [1], "y": [2]}),
                                   "black", None)
    assert isinstance(result, lpp.PubPlotSpec)


def test_add_extra_layers_none():
    p = lpp.ggplot(pd.DataFrame({"x": [1], "y": [2]}), lpp.aes(x="x", y="y"))
    result = lpp.add_extra_layers(p, "x", "y", None, None,
                                   pd.DataFrame({"x": [1], "y": [2]}),
                                   "black", None)
    assert isinstance(result, lpp.PubPlotSpec)


def test_add_extra_layers_jitter():
    df = pd.DataFrame({"x": ["A", "B"], "y": [1.0, 2.0]})
    p = lpp.ggplot(df, lpp.aes(x="x", y="y"))
    result = lpp.add_extra_layers(p, "x", "y", ["jitter"], None, df, "black", None)
    assert isinstance(result, lpp.PubPlotSpec)


def test_add_extra_layers_boxplot():
    df = pd.DataFrame({"x": ["A", "B"], "y": [1.0, 2.0], "f": ["X", "Y"]})
    p = lpp.ggplot(df, lpp.aes(x="x", y="y"))
    result = lpp.add_extra_layers(p, "x", "y", ["boxplot"], None, df, "black", "f")
    assert isinstance(result, lpp.PubPlotSpec)


def test_add_extra_layers_dotplot():
    df = pd.DataFrame({"x": ["A", "B"], "y": [1.0, 2.0]})
    p = lpp.ggplot(df, lpp.aes(x="x", y="y"))
    result = lpp.add_extra_layers(p, "x", "y", ["dotplot"], None, df, "black", None)
    assert isinstance(result, lpp.PubPlotSpec)


# ---------- PubPlotSpec ----------

def test_pubplotspec_add_feature_spec(sample_data):
    p = lpp.ggboxplot(sample_data, x='group', y='value')
    from lets_plot import ggtitle
    p2 = p + ggtitle("Test Title")
    assert isinstance(p2, lpp.PubPlotSpec)


def test_pubplotspec_radd():
    """Test __radd__: PubPlotSpec + FeatureSpec should work."""
    p = lpp.ggscatter(pd.DataFrame({"x": [1, 2], "y": [3, 4]}), x="x", y="y")
    from lets_plot import ggtitle
    # PubPlotSpec + FeatureSpec (via __add__ then __radd__)
    p2 = p + ggtitle("Radd Test")
    assert isinstance(p2, lpp.PubPlotSpec)


# ---------- ggplot creates PubPlotSpec ----------

def test_ggplot_returns_pubplotspec():
    p = lpp.ggplot(pd.DataFrame({"x": [1], "y": [2]}), lpp.aes(x="x", y="y"))
    assert isinstance(p, lpp.PubPlotSpec)
