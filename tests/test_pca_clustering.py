"""Test PCA clustering visualization with confidence ellipses using the
new ``ggscatter`` API with ``ellipse=True``.

PCA is computed with numpy/SVD and visualized via ``ggscatter`` with
built-in confidence ellipses, correlation annotation, and marginal rugs.
"""
import os
import numpy as np
import pandas as pd
import pytest

import letspubpy as lpp
from lets_plot import ggsave


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_cluster_data(n_per_group=30, n_features=6, seed=42):
    """Generate synthetic multivariate data with three distinct clusters."""
    rng = np.random.default_rng(seed)
    means = [
        np.array([2.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([-1.5, 1.5, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, -2.0, 1.0, 0.0, 0.0, 0.0]),
    ]
    covs = [
        np.diag([1.0, 0.8, 0.6, 0.5, 0.4, 0.3]),
        np.diag([0.7, 1.2, 0.5, 0.4, 0.3, 0.2]),
        np.diag([1.1, 0.9, 0.7, 0.5, 0.4, 0.4]),
    ]
    labels = ["A", "B", "C"]

    Xs, ys = [], []
    for m, c, lab in zip(means, covs, labels):
        Xs.append(rng.multivariate_normal(m, c, size=n_per_group))
        ys.extend([lab] * n_per_group)

    X = np.vstack(Xs)
    y = np.array(ys)
    return X, y


def pca_2d(X):
    """Standardized PCA via SVD; returns first two PCs and explained variance ratio."""
    Xs = (X - X.mean(axis=0)) / X.std(axis=0, ddof=0)
    U, S, Vt = np.linalg.svd(Xs, full_matrices=False)
    PCs = Xs @ Vt.T
    explained = (S ** 2) / np.sum(S ** 2)
    return PCs[:, :2], explained[:2]


def build_pca_plot(df, explained, level=0.95):
    """Construct the publication-ready PCA scatter with confidence ellipses.

    Uses the new ``ggscatter`` API with built-in ``ellipse``, ``rug``, and
    ``cor`` parameters, mirroring ggpubr's convenience features.
    """
    p = lpp.ggscatter(
        df,
        x="PC1",
        y="PC2",
        color="group",
        fill="group",
        palette="npg",
        size=3,
        ellipse=True,
        ellipse_level=level,
        ellipse_type="norm",
        ellipse_alpha=0.15,
        rug=True,
        cor=True,
        cor_method="pearson",
        cor_size=12,
        aspect_ratio=1,
        title=f"PCA Clustering with {int(level * 100)}% Confidence Ellipses",
        xlab=f"PC1 ({explained[0] * 100:.1f}%)",
        ylab=f"PC2 ({explained[1] * 100:.1f}%)",
    )
    return p


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def pca_data():
    X, y = make_cluster_data()
    PCs, explained = pca_2d(X)
    df = pd.DataFrame({"PC1": PCs[:, 0], "PC2": PCs[:, 1], "group": y})
    return df, explained


@pytest.fixture
def pca_plot(pca_data):
    df, explained = pca_data
    return build_pca_plot(df, explained, level=0.95), df


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_pca_data_shape():
    X, y = make_cluster_data()
    assert X.shape == (90, 6)
    assert len(y) == 90
    assert set(np.unique(y)) == {"A", "B", "C"}


def test_pca_explained_variance():
    X, _ = make_cluster_data()
    _, explained = pca_2d(X)
    assert explained.shape == (2,)
    assert explained.sum() < 1.0
    assert explained[0] > explained[1] > 0


def test_confidence_ellipse_shape():
    """Test the library-level helper from letspubpy."""
    rng = np.random.default_rng(0)
    pts = rng.multivariate_normal([0, 0], np.eye(2), size=50)
    ell = lpp.confidence_ellipse_points(
        pts.mean(axis=0), np.cov(pts.T), n_points=80, level=0.95
    )
    assert ell.shape == (80, 2)


def test_pca_plot_structure(pca_plot):
    p, _ = pca_plot
    assert isinstance(p, lpp.PubPlotSpec)
    p_dict = p.as_dict()
    assert p_dict["kind"] == "plot"

    geoms = [layer.get("geom") for layer in p_dict["layers"]]
    assert "point" in geoms, "Scatter points layer is missing"
    assert "polygon" in geoms, "Confidence ellipse polygon layer is missing"

    # Polygon layer should have group mapping
    polygon_layers = [l for l in p_dict["layers"] if l.get("geom") == "polygon"]
    assert len(polygon_layers) == 1
    poly_mapping = polygon_layers[0].get("mapping", {})
    assert poly_mapping.get("group") == "group"


def test_pca_plot_cor_text(pca_plot):
    p, _ = pca_plot
    p_dict = p.as_dict()
    text_layers = [l for l in p_dict["layers"] if l.get("geom") == "text"]
    assert len(text_layers) > 0
    # Should have correlation annotation
    labels = [str(l.get("label", "")) for l in text_layers]
    assert any("Pearson" in label or "R" in label for label in labels)


def test_pca_plot_renders_to_svg(pca_plot, tmp_path):
    p, _ = pca_plot
    out = tmp_path / "pca_clustering.svg"
    ggsave(p, str(out))
    assert out.exists()
    assert out.stat().st_size > 0


def test_pca_plot_saves_demo_svg(pca_plot):
    """Save a demo SVG into ``images/`` for visual inspection by the user."""
    p, _ = pca_plot
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")
    os.makedirs(images_dir, exist_ok=True)
    out = os.path.join(images_dir, "pca_clustering_example.svg")
    ggsave(p, out)
    assert os.path.exists(out)


if __name__ == "__main__":
    X, y = make_cluster_data()
    PCs, explained = pca_2d(X)
    df = pd.DataFrame({"PC1": PCs[:, 0], "PC2": PCs[:, 1], "group": y})
    p = build_pca_plot(df, explained, level=0.95)

    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")
    os.makedirs(images_dir, exist_ok=True)
    out = os.path.join(images_dir, "pca_clustering_example.svg")
    ggsave(p, out)
    print(f"Saved: {out}")
