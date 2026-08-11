# Re-expose all of lets-plot
from lets_plot import *

# Overwrite with our custom extensions
from .plots import (
    PubPlotSpec,
    ggplot,
    ggboxplot,
    ggviolin,
    ggdotplot,
    ggstripchart,
    ggbarplot,
    ggline,
    ggscatter,
    gghistogram,
    ggdensity,
    ggpie,
    ggdonutchart,
    ggqqplot,
    ggecdf,
    ggcorr,
    ggheatmap,
    ggclustergram,
    ggclustervis,
    ggheatmap_cluster,
    visCluster,
    ggvisCluster,
    sim_pseudotime_data,
    sim_pseudotime,
    visPseudotime,
    ggpseudotime,
    gsea_plot,
    visGSEA,
    gggsea,
    gggsea_plot,
    blitzgsea_plot,
    visBlitzGSEA,
    ggblitzgsea,
    compute_heat_blocks,
    sim_gsea_data,
    sim_enrichment_data,
    visEnrichLollipop,
    ggenrich_lollipop,
    gglollipop_enrich,
    visEnrichNetwork,
    cnetplot,
    visCnetplot,
    ggenrich_network,
    ggcnetplot,
    rremove,
    ggpar,
    confidence_ellipse_points,
    build_ellipse_df,
    compute_correlation,
    get_color_fill_aes_and_params,
    apply_labels_and_theme,
    add_extra_layers
)
from .theme import theme_pubr, scale_color_pubr, scale_fill_pubr
from .stats import stat_compare_means, add_stat_compare_means, stat_cor, stat_regline_equation
from .arrange import ggarrange
from .prism import theme_prism, scale_color_prism, scale_colour_prism, scale_fill_prism, scale_shape_prism

# Dynamically construct __all__ to include lets_plot's original exports (with ggplot overridden) and our new functions
import lets_plot as _lp
__all__ = list(_lp.__all__)
if 'ggplot' in __all__:
    __all__.remove('ggplot')

__all__.extend([
    'ggplot', 'PubPlotSpec', 'ggboxplot', 'ggviolin', 'ggdotplot', 'ggstripchart',
    'ggbarplot', 'ggline', 'ggscatter', 'gghistogram', 'ggdensity', 'ggpie',
    'ggdonutchart', 'ggqqplot', 'ggecdf', 'ggcorr',
    'ggheatmap', 'ggclustergram', 'ggclustervis', 'ggheatmap_cluster', 'visCluster', 'ggvisCluster',
    'sim_pseudotime_data', 'sim_pseudotime', 'visPseudotime', 'ggpseudotime',
    'gsea_plot', 'visGSEA', 'gggsea', 'gggsea_plot', 'blitzgsea_plot', 'visBlitzGSEA', 'ggblitzgsea',
    'compute_heat_blocks', 'sim_gsea_data',
    'sim_enrichment_data', 'visEnrichLollipop', 'ggenrich_lollipop', 'gglollipop_enrich',
    'visEnrichNetwork', 'cnetplot', 'visCnetplot', 'ggenrich_network', 'ggcnetplot',
    'rremove', 'ggpar',
    'theme_pubr', 'scale_color_pubr', 'scale_fill_pubr',
    'stat_compare_means', 'add_stat_compare_means', 'stat_cor', 'stat_regline_equation',
    'ggarrange',
    'theme_prism', 'scale_color_prism', 'scale_colour_prism', 'scale_fill_prism', 'scale_shape_prism',
    'confidence_ellipse_points', 'build_ellipse_df', 'compute_correlation',
    'get_color_fill_aes_and_params', 'apply_labels_and_theme', 'add_extra_layers'
])

