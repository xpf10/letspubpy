from lets_plot import (
    theme_classic,
    theme,
    element_line,
    element_text,
    element_rect,
    element_blank,
    scale_color_manual,
    scale_fill_manual
)

# Publication color palettes from ggsci / ggpubr
PALETTES = {
    "npg": ["#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F", "#8491B3", "#91D1C2", "#DC0000", "#7E6148", "#B09C85"],
    "aaas": ["#3B4992", "#EE0000", "#008B45", "#631879", "#008280", "#BB0021", "#5F559B", "#A20056", "#808080", "#1B1919"],
    "nejm": ["#BC3C29", "#0072B5", "#E18727", "#20854E", "#7876B1", "#6F99AD", "#FFDC91", "#EE4C97"],
    "jama": ["#374E55", "#DF8F44", "#00A1D5", "#B24745", "#79AF97", "#6A6599", "#80796B"],
    "jco": ["#0073C2", "#EFC000", "#868686", "#CD534C", "#7AA6C2", "#8F7700", "#B3B3B3", "#3B3B3B", "#858482", "#1A1A1A"],
    "d3": ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD", "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"],
    "lancet": ["#00468B", "#ED0000", "#42B540", "#0099B4", "#925E9F", "#FDAF91", "#AD002A", "#ADB6B6"],
    "locuszoom": ["#3182BD", "#E6550D", "#31A354", "#756BB1", "#636363", "#FD8D3C", "#A1D99B", "#BCBDDC"],
    "simpsons": ["#FED439", "#709AE1", "#8A9197", "#D2AF81", "#FD7446", "#D5E4A2", "#197EC0", "#F05C3B", "#46732E", "#71130E"],
    "tron": ["#FF0055", "#00FFCC", "#00CCFF", "#FFFF00", "#FF00FF", "#00FF00"],
}

def theme_pubr(base_size=12, base_family=None, legend="top", border=False):
    """
    Create a publication-ready theme similar to ggpubr's theme_pubr().
    
    Parameters
    ----------
    base_size : int, default=12
        Base font size.
    base_family : str, default=None
        Base font family.
    legend : str, default="top"
        Legend position ("top", "bottom", "left", "right", "none").
    border : bool, default=False
        If True, draws a border around the panel.
    """
    t = theme_classic()
    
    # Adjust classic theme parameters to fit publication standards
    t += theme(
        legend_position=legend,
        legend_background=element_blank(),
        legend_title=element_text(size=base_size, face='bold', family=base_family),
        legend_text=element_text(size=base_size - 1, family=base_family),
        plot_title=element_text(size=base_size + 2, face='bold', hjust=0.5, family=base_family),
        plot_subtitle=element_text(size=base_size, face='italic', hjust=0.5, family=base_family),
        plot_caption=element_text(size=base_size - 2, hjust=1, family=base_family),
        axis_title=element_text(size=base_size, face='bold', family=base_family),
        axis_text=element_text(size=base_size - 1, family=base_family),
        axis_line=element_line(color='black', size=0.8),
        axis_ticks=element_line(color='black', size=0.8),
        panel_grid_major=element_blank(),
        panel_grid_minor=element_blank()
    )
    
    if border:
        t += theme(
            panel_background=element_rect(color='black', fill='#00000000', size=1)
        )
        
    return t

def get_palette(palette_name, n=None):
    """Resolve a palette name or list to a list of colors."""
    if isinstance(palette_name, list):
        colors = palette_name
    else:
        colors = PALETTES.get(str(palette_name).lower(), [palette_name])
    if n is not None and n > len(colors):
        colors = (colors * ((n // len(colors)) + 1))[:n]
    return colors

def scale_color_pubr(palette="npg", **kwargs):
    """Scale color manually using a pubr palette."""
    return scale_color_manual(values=get_palette(palette), **kwargs)

def scale_fill_pubr(palette="npg", **kwargs):
    """Scale fill manually using a pubr palette."""
    return scale_fill_manual(values=get_palette(palette), **kwargs)
