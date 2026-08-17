"""Generate all example plot images for the documentation."""
import os
import warnings
import numpy as np
import pandas as pd
import letspubpy as lpp
from lets_plot import ggsave, LetsPlot

warnings.filterwarnings("ignore")
LetsPlot.setup_html()

# Output directory
IMG_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(IMG_DIR, exist_ok=True)


def save(p, name, w=800, h=500):
    path = os.path.join(IMG_DIR, f"{name}.png")
    ggsave(p, filename=f"{name}.png", path=IMG_DIR, w=w, h=h, unit="px")
    print(f"  saved: {path}")


# ── Shared data ────────────────────────────────────────────────────────────────
np.random.seed(42)
N = 30

df_box = pd.DataFrame({
    "group": ["Control"] * N + ["Treat A"] * N + ["Treat B"] * N,
    "expression": np.concatenate([
        np.random.normal(1.0, 0.4, N),
        np.random.normal(1.8, 0.5, N),
        np.random.normal(1.4, 0.3, N),
    ]),
})

df_violin = pd.DataFrame({
    "group": ["A"] * 50 + ["B"] * 50 + ["C"] * 50,
    "value": np.concatenate([
        np.random.normal(0, 1, 50),
        np.random.normal(2, 1.5, 50),
        np.random.normal(-1, 0.8, 50),
    ]),
})

df_bar = pd.DataFrame({
    "treatment": ["A"] * N + ["B"] * N + ["C"] * N,
    "value": np.concatenate([
        np.random.normal(0, 1, N),
        np.random.normal(1.5, 1, N),
        np.random.normal(0.5, 1, N),
    ]),
})

df_line = pd.DataFrame({
    "time": ["Day 1"] * 20 + ["Day 3"] * 20 + ["Day 7"] * 20,
    "treatment": (["Ctrl"] * 10 + ["Drug"] * 10) * 3,
    "value": np.concatenate([
        np.random.normal(0, 1, 10), np.random.normal(2, 1, 10),
        np.random.normal(0.5, 1, 10), np.random.normal(3, 1, 10),
        np.random.normal(1, 1, 10), np.random.normal(4, 1, 10),
    ]),
})

x_scatter = np.random.uniform(1, 10, 50)
y_scatter = x_scatter * 1.5 + np.random.normal(0, 1.5, 50)
df_scatter = pd.DataFrame({"x": x_scatter, "y": y_scatter})

df_scatter_group = pd.DataFrame({
    "x": np.concatenate([
        np.random.normal(0, 1, N), np.random.normal(3, 1, N), np.random.normal(-2, 1, N)
    ]),
    "y": np.concatenate([
        np.random.normal(0, 1, N), np.random.normal(3, 1, N), np.random.normal(4, 1, N)
    ]),
    "group": ["A"] * N + ["B"] * N + ["C"] * N,
})

df_hist = pd.DataFrame({
    "value": np.concatenate([
        np.random.normal(0, 1, 100), np.random.normal(2, 1, 100)
    ]),
    "group": ["A"] * 100 + ["B"] * 100,
})

df_density = df_hist.copy()

df_pie = pd.DataFrame({
    "category": ["A", "B", "C", "D"],
    "count": [30, 25, 20, 25],
})

df_qq = pd.DataFrame({"value": np.random.normal(0, 1, 200)})
df_qq_group = pd.DataFrame({
    "value": np.concatenate([
        np.random.normal(0, 1, 100), np.random.normal(2, 1, 100)
    ]),
    "group": ["A"] * 100 + ["B"] * 100,
})

df_ecdf = pd.DataFrame({
    "value": np.concatenate([
        np.random.normal(0, 1, 100), np.random.normal(2, 1, 100)
    ]),
    "group": ["A"] * 100 + ["B"] * 100,
})

df_corr = pd.DataFrame({
    "height": np.random.normal(170, 10, 100),
    "weight": np.random.normal(70, 15, 100),
    "age": np.random.normal(30, 5, 100),
    "score": np.random.normal(80, 10, 100),
})

df_pca = df_scatter_group.rename(columns={"x": "PC1", "y": "PC2"})


# ── Generate plots ─────────────────────────────────────────────────────────────
print("Generating images...")

# 1. Boxplot
p = lpp.ggboxplot(
    df_box, x="group", y="expression",
    fill="group", palette="npg", add="jitter",
    title="Gene Expression Analysis",
)
save(p, "boxplot_basic")

p = lpp.ggboxplot(
    df_box, x="group", y="expression",
    fill="group", palette="npg", add="jitter",
    title="With Statistical Comparisons",
) + lpp.stat_compare_means(
    comparisons=[("Control", "Treat A"), ("Treat A", "Treat B")],
    method="wilcoxon", color="red",
)
save(p, "boxplot_stats")

# 2. Violin
p = lpp.ggviolin(
    df_violin, x="group", y="value",
    fill="group", palette="npg", add="boxplot",
    title="Violin with Embedded Boxplot",
)
save(p, "violin_basic")

# 3. Bar plot
p = lpp.ggbarplot(
    df_bar, x="treatment", y="value",
    fill="treatment", palette="npg", add="mean_se",
    title="Bar Plot with Error Bars",
)
save(p, "barplot_basic")

# 4. Line plot
p = lpp.ggline(
    df_line, x="time", y="value",
    color="treatment", palette="npg", add="mean_se",
    title="Line Plot with Error Bars",
)
save(p, "lineplot_basic")

# 5. Scatter
p = lpp.ggscatter(
    df_scatter, x="x", y="y", color="#3C5488",
    add="reg.line", confint=True,
    title="Scatter with Regression Line",
)
save(p, "scatter_basic")

p = lpp.ggscatter(
    df_scatter_group, x="x", y="y",
    color="group", fill="group", palette="npg", size=3,
    ellipse=True, ellipse_level=0.95, ellipse_type="norm", ellipse_alpha=0.15,
    title="Grouped Scatter with Confidence Ellipses",
)
save(p, "scatter_ellipse")

p = lpp.ggscatter(
    df_scatter, x="x", y="y", color="#3C5488",
    add="reg.line", confint=True,
    title="Scatter with Correlation Annotation",
) + lpp.stat_cor(method="pearson", size=12)
save(p, "scatter_cor")

# 6. Histogram
p = lpp.gghistogram(
    df_hist, x="value", fill="group", palette="npg",
    bins=30,
    title="Grouped Histogram",
)
save(p, "histogram_basic")

# 7. Density
p = lpp.ggdensity(
    df_density, x="value", fill="group", palette="npg",
    title="Grouped Density Plot",
)
save(p, "density_basic")

# 8. Pie & Donut
p = lpp.ggpie(
    df_pie, x="category", label="count",
    fill="category", palette="npg",
    title="Pie Chart",
)
save(p, "pie_basic", w=600, h=600)

p = lpp.ggdonutchart(
    df_pie, x="category", label="count",
    fill="category", palette="npg", hole=0.4,
    title="Donut Chart",
)
save(p, "donut_basic", w=600, h=600)

# 9. Q-Q plot
p = lpp.ggqqplot(
    df_qq, x="value", add="qqline",
    title="Q-Q Plot (Normal Data)",
)
save(p, "qqplot_basic")

p = lpp.ggqqplot(
    df_qq_group, x="value",
    color="group", fill="group", add="qqline", palette="npg",
    title="Grouped Q-Q Plot",
)
save(p, "qqplot_group")

# 10. ECDF
p = lpp.ggecdf(
    df_ecdf, x="value", color="group", palette="npg",
    title="Empirical CDF",
)
save(p, "ecdf_basic")

# 11. Correlation heatmap
p = lpp.ggcorr(
    df_corr, method="pearson",
    p_low="*", p_high="ns",
    title="Correlation Matrix",
)
save(p, "corrplot_basic", w=600, h=600)

# 12. PCA clustering
p = lpp.ggscatter(
    df_pca, x="PC1", y="PC2",
    color="group", fill="group", palette="npg", size=3,
    ellipse=True, ellipse_level=0.95, ellipse_type="norm", ellipse_alpha=0.15,
    rug=True, cor=True, cor_method="pearson", cor_size=12,
    title="PCA Clustering with 95% Confidence Ellipses",
)
save(p, "pca_clustering", w=700, h=600)

# 13. Clustered Heatmap
np.random.seed(42)
genes = [f"Gene_{i+1}" for i in range(12)]
samples = [f"Ctrl_{j+1}" for j in range(4)] + [f"Treat_{j+1}" for j in range(4)]
mat_heat = pd.DataFrame(np.random.randn(12, 8), index=genes, columns=samples)
p = lpp.ggclustervis(
    mat_heat, scale="row", cluster_rows=True, cluster_cols=True,
    palette="bwr", title="Clustered Gene Expression Heatmap",
    xlab="Samples", ylab="Genes"
)
save(p, "heatmap_clustered", w=700, h=550)

# 14. ClusterGVis Dual View
timepoints = ["0h", "2h", "6h", "12h", "24h", "48h"]
t = np.linspace(0, 2 * np.pi, 6)
data_trend = [np.sin(t) + np.random.normal(0, 0.2, 6) if i < 12 else np.cos(t) + np.random.normal(0, 0.2, 6) for i in range(24)]
df_trend = pd.DataFrame(data_trend, index=[f"Gene_{i+1:02d}" for i in range(24)], columns=timepoints)
p = lpp.visCluster(
    df_trend, n_clusters=4, scale="row", plot_type="both",
    trend_position="left", palette="bwr", cluster_palette="npg",
    title="ClusterGVis Expression Dynamics"
)
save(p, "viscluster_basic", w=900, h=600)

# 15. Pseudotime Trajectory Heatmap
df_pseudo = lpp.sim_pseudotime_data(n_genes=80, n_pts=40, n_clusters=4)
p = lpp.visPseudotime(
    data=df_pseudo, n_clusters=4, scale="row",
    palette="bwr", cluster_palette="npg",
    title="Single-Cell Pseudotime Trajectory Heatmap"
)
save(p, "pseudotime_basic", w=800, h=600)

# 16. GSEA Running Score Plot
res_data, term, rnk = lpp.sim_gsea_data(n_genes=120, n_hits=15, nes=1.92, term="KEGG_CELL_CYCLE")
p = lpp.visGSEA(res_data, term=term, rnk=rnk)
save(p, "gsea_basic", w=700, h=500)

# 17. Enrichment Lollipop Chart
df_enrich = lpp.sim_enrichment_data(n_terms=10)
p = lpp.visEnrichLollipop(df_enrich, top_n=8, title="Pathway Enrichment Lollipop Chart")
save(p, "enrichment_lollipop", w=750, h=500)

# 18. Clustered Concept Network
p = lpp.visEnrichNetwork(df_enrich, top_n=5, cluster_pathways=True, show_hulls=True, title="Pathway-Gene Concept Network (cnetplot)")
save(p, "enrichment_network", w=800, h=650)

# 19. Volcano Plot
p = lpp.ggvolcano(fc_cutoff=1.0, p_cutoff=0.05, top_n=10, title="RNA-seq Differential Expression Volcano Plot")
save(p, "volcano_basic", w=750, h=550)

# 20. Raincloud Plot
p = lpp.ggraincloud(palette="npg", title="Multimodal Distribution Raincloud Plot")
save(p, "raincloud_basic", w=750, h=500)

# 21. Kaplan-Meier Survival Plot
p = lpp.ggsurvplot(title="Kaplan-Meier Overall Survival Curve", palette="npg")
save(p, "survival_basic", w=750, h=550)

# 22. Forest Plot
p = lpp.ggforest(title="Meta-Analysis Hazard Ratios (95% CI)")
save(p, "forest_basic", w=800, h=500)

# 23. ROC Curve
p = lpp.ggroc(title="Multi-Model ROC Diagnostic Comparison", palette="npg")
save(p, "roc_basic", w=700, h=550)

# 24. Dose-Response IC50
p = lpp.ggdoseresponse(title="Sigmoidal 4PL Dose-Response IC50 Curve", palette="npg")
save(p, "doseresponse_basic", w=750, h=500)

# 25. Waterfall Plot
p = lpp.ggwaterfall(title="Oncology RECIST Tumor Burden Waterfall Plot", palette="npg")
save(p, "waterfall_basic", w=800, h=500)

# 26. GWAS Manhattan Plot
p = lpp.ggmanhattan(title="GWAS Genome-Wide Association Manhattan Plot")
save(p, "manhattan_basic", w=900, h=500)

# 27. Bland-Altman Plot
p = lpp.ggblandaltman(title="Bland-Altman Clinical Measurement Agreement Plot")
save(p, "blandaltman_basic", w=750, h=500)

# 28. Radar / Spider Chart
p = lpp.ggradar(title="Multi-Metric Phenotypic Profile Radar Chart", palette="npg")
save(p, "radar_basic", w=650, h=600)

# 29. UpSet Plot
p = lpp.ggupset(title="UpSet Multi-Set Overlap Analysis")
save(p, "upset_basic", w=800, h=600)

print("\nAll images generated successfully!")
