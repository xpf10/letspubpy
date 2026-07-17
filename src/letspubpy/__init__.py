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
    ggdonutchart
)
from .theme import theme_pubr, scale_color_pubr, scale_fill_pubr
from .stats import stat_compare_means, add_stat_compare_means
from .arrange import ggarrange

# Dynamically construct __all__ to include lets_plot's original exports (with ggplot overridden) and our new functions
import lets_plot as _lp
__all__ = list(_lp.__all__)
if 'ggplot' in __all__:
    __all__.remove('ggplot')

__all__.extend([
    'ggplot', 'PubPlotSpec', 'ggboxplot', 'ggviolin', 'ggdotplot', 'ggstripchart',
    'ggbarplot', 'ggline', 'ggscatter', 'gghistogram', 'ggdensity', 'ggpie',
    'ggdonutchart', 'theme_pubr', 'scale_color_pubr', 'scale_fill_pubr',
    'stat_compare_means', 'add_stat_compare_means', 'ggarrange'
])
