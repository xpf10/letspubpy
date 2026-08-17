# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-08-17

### Added

- **Heatmaps & Clustering Suite**:
  - `ggheatmap` — Heatmap with row/column hierarchical clustering and Z-score scaling.
  - `ggclustervis` / `ggclustergram` — Hierarchical clustered heatmaps.
  - `visCluster` — ClusterGVis-style dual view (clustered heatmap + line trend plots).
  - `visPseudotime` — Single-cell Monocle-style pseudotime trajectory heatmaps.
  - `visGSEA` / `blitzgsea_plot` — GSEA running score curve with barcode ribbons.
  - `visEnrichLollipop` — Pathway enrichment analysis lollipop charts.
  - `visEnrichNetwork` / `cnetplot` — Pathway-gene concept network with convex hull clustering.
- **Scientific & Clinical Plots Suite**:
  - `ggvolcano` / `visVolcano` — RNA-seq / Proteomics differential expression volcano plot with threshold lines and top gene labels.
  - `ggraincloud` / `visRaincloud` — Multimodal raincloud plot (half-violin + boxplot + jittered points).
  - `ggsurvplot` / `visSurvival` — Kaplan-Meier survival curves with Greenwood 95% CIs, censored markers, and automated log-rank test $p$-values.
  - `ggforest` / `visForest` — Meta-analysis & Cox/Logistic regression forest plots with aligned table labels.
  - `ggroc` / `visROC` — Multi-model ROC and Precision-Recall (PRC) curves with automated trapezoidal AUC and Youden's J optimal cutpoint detection.
  - `ggdoseresponse` / `ggic50` — Non-linear sigmoidal 4-parameter logistic (4PL) regression curve fitting and IC50/EC50 estimation.
  - `ggwaterfall` / `visWaterfall` — Oncology RECIST tumor burden waterfall plot with PR/PD threshold lines.
  - `ggmanhattan` / `visManhattan` — GWAS Manhattan plot with alternating chromosome colors and lead SNP annotations.
  - `ggblandaltman` / `visBlandAltman` — Bland-Altman method agreement plot with Mean Bias and 95% Limits of Agreement.
  - `ggradar` / `visRadar` — Multi-metric phenotypic radar / spider charts with concentric polygonal grids.
  - `ggupset` / `visUpSet` — UpSet multi-set intersection bar chart and connected dot matrix.
- **Synthetic Data Generators**:
  - `sim_volcano_data`, `sim_raincloud_data`, `sim_survival_data`, `sim_forest_data`, `sim_roc_data`, `sim_doseresponse_data`, `sim_waterfall_data`, `sim_gwas_data`, `sim_blandaltman_data`, `sim_radar_data`, `sim_upset_data`.
- **Documentation**:
  - 15 new dedicated documentation pages and 29 rendered example images.
- **Unit Tests**:
  - Expanded test suite to 158 tests with 100% pass rate.

## [0.1.0] - 2025-08-07

### Added

- Initial release of letspubpy
- High-level plot functions: `ggboxplot`, `ggviolin`, `ggdotplot`, `ggstripchart`, `ggbarplot`, `ggline`, `ggscatter`, `gghistogram`, `ggdensity`, `ggpie`, `ggdonutchart`
- `ggqqplot` — Q-Q normality plots
- `ggecdf` — Empirical CDF plots
- `ggcorr` — Correlation heatmaps
- `stat_compare_means` — Statistical significance brackets
- `stat_cor` — Correlation annotations
- `stat_regline_equation` — Regression equation annotations
- `ggarrange` — Multi-panel figure layout
- `rremove` — Remove plot elements
- `ggpar` — Plot appearance customization
- `theme_pubr` — Publication-ready theme
- `theme_prism` — GraphPad Prism-like theme
- Journal color palettes (npg, aaas, nejm, jama, jco, lancet, etc.)
- Confidence ellipse support for scatter plots
- Rug plot support for scatter plots
- Correlation annotations on scatter plots
- PCA clustering visualization with confidence intervals
- Comprehensive test suite (161 tests)
- Full documentation website with MkDocs

### Dependencies

- lets-plot >= 4.11.0
- numpy >= 2.2.6
- pandas >= 2.3.3
- scipy >= 1.15.3
