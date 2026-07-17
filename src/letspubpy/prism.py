from lets_plot import (
    theme,
    element_line,
    element_rect,
    element_text,
    element_blank,
    scale_color_manual,
    scale_fill_manual,
    scale_shape_manual
)
from .prism_palettes import THEME_PALETTES, COLOUR_PALETTES, FILL_PALETTES, SHAPE_PALETTES

def theme_prism(
    palette="black_and_white",
    base_size=14,
    base_family="sans",
    base_fontface="bold",
    border=False
):
    """
    A collection of themes that mirror the color schemes available in GraphPad Prism.

    Parameters
    ----------
    palette : str, default="black_and_white"
        Palette name. Use `list(THEME_PALETTES.keys())` to show all valid names.
    base_size : int or float, default=14
        Base font size, in points.
    base_family : str, default="sans"
        Base font family.
    base_fontface : str, default="bold"
        Base font face. One of: "plain", "bold", "italic", "bold_italic".
    border : bool, default=False
        Should a border be drawn around the plot?
    
    Returns
    -------
    FeatureSpec
        A lets-plot theme object.
    """
    if palette not in THEME_PALETTES:
        raise ValueError(
            f"The palette '{palette}' does not exist. "
            f"Valid palette names: {list(THEME_PALETTES.keys())}"
        )
    
    colours = THEME_PALETTES[palette]
    
    base_line_size = base_size / 14.0
    base_rect_size = base_size / 14.0
    
    # Border vs line options (avoiding 'none' parsing issues in SVGs)
    if border:
        panel_border = element_rect(fill='#00000000', color=colours.get("axisColor", "#000000"), size=base_rect_size)
        axis_line = element_blank()
    else:
        panel_border = element_blank()
        axis_line = element_line(color=colours.get("axisColor", "#000000"), size=base_line_size)

    # Panel background
    if palette == "office":
        panel_background = element_rect(fill=colours.get("plottingAreaColor", "#FFFFFF"), color='#00000000')
    else:
        panel_background = element_blank()

    t = theme(
        # Base lines and rects defaults
        line=element_line(color=colours.get("axisColor", "#000000"), size=base_line_size),
        rect=element_rect(color=colours.get("axisColor", "#000000"), size=base_rect_size, fill="white"),
        text=element_text(
            family=base_family,
            face=base_fontface,
            color=colours.get("graphTitleColor", "#000000"),
            size=base_size
        ),
        
        # Axis lines and ticks
        axis_line=axis_line,
        axis_line_x=None,
        axis_line_y=None,
        axis_text=element_text(color=colours.get("axisLabelColor", "#000000"), size=base_size * 0.95),
        axis_title=element_text(color=colours.get("axisTitleColor", "#000000")),
        
        # Legend settings
        legend_background=element_blank(),
        legend_key=element_blank(),
        legend_title=element_blank(),
        legend_text=element_text(size=base_size * 0.8, face="plain"),
        
        # Grid settings
        panel_background=panel_background,
        panel_border=panel_border,
        panel_grid=element_blank(),
        panel_grid_major=element_blank(),
        panel_grid_minor=element_blank(),
        
        # Strip settings
        strip_background=element_blank(),
        strip_text=element_text(color=colours.get("axisTitleColor", "#000000"), size=base_size * 0.8),
        
        # Plot background and titles
        plot_background=element_rect(fill=colours.get("pageBackgroundColor", "#FFFFFF"), color='#00000000'),
        plot_title=element_text(size=base_size * 1.2, face=base_fontface),
        plot_subtitle=element_text(size=base_size, face=base_fontface),
        plot_caption=element_text(size=base_size * 0.8, face="plain")
    )
    
    return t

def scale_color_prism(palette="colors", **kwargs):
    """
    Discrete color scale that uses palettes mirroring the color schemes in GraphPad Prism.
    """
    if palette not in COLOUR_PALETTES:
        raise ValueError(
            f"The color palette '{palette}' does not exist. "
            f"Valid color palette names: {list(COLOUR_PALETTES.keys())}"
        )
    return scale_color_manual(values=COLOUR_PALETTES[palette], **kwargs)

# Alias for scale_color_prism
scale_colour_prism = scale_color_prism

def scale_fill_prism(palette="colors", **kwargs):
    """
    Discrete fill scale that uses palettes mirroring the color schemes in GraphPad Prism.
    """
    if palette not in FILL_PALETTES:
        raise ValueError(
            f"The fill palette '{palette}' does not exist. "
            f"Valid fill palette names: {list(FILL_PALETTES.keys())}"
        )
    return scale_fill_manual(values=FILL_PALETTES[palette], **kwargs)

def scale_shape_prism(palette="default", **kwargs):
    """
    Discrete shape scale that uses marker shape sequences mirroring GraphPad Prism.
    """
    if palette not in SHAPE_PALETTES:
        raise ValueError(
            f"The shape palette '{palette}' does not exist. "
            f"Valid shape palette names: {list(SHAPE_PALETTES.keys())}"
        )
    return scale_shape_manual(values=SHAPE_PALETTES[palette], **kwargs)
