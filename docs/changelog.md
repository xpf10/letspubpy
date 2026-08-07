# Changelog

All notable changes to this project will be documented in this file.

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
