# Themes & Color Palettes

letspubpy provides publication-ready themes and journal color palettes.

## Default Theme: theme_pubr

```python
import letspubpy as lpp

# Default usage (automatically applied to all plots)
p = lpp.ggboxplot(df, x='group', y='value', fill='group')

# Customize theme parameters
p = lpp.ggboxplot(
    df, x='group', y='value',
    ggtheme=lpp.theme_pubr(
        base_size=14,
        base_family='sans',
        legend='bottom',
        border=True
    )
)
```

## Journal Color Palettes

Apply color schemes matching top journals:

| Palette Name | Description |
|-------------|-------------|
| `npg` | Nature Publishing Group |
| `aaas` | American Association for the Advancement of Science |
| `nejm` | New England Journal of Medicine |
| `jama` | Journal of the American Medical Association |
| `jco` | Journal of Clinical Oncology |
| `lancet` | Lancet |
| `locuszoom` | LocusZoom |
| `simpsons` | The Simpsons |
| `tron` | Tron-inspired |

```python
# Apply to any plot via palette parameter
p = lpp.ggboxplot(df, x='group', y='value', fill='group', palette='npg')
p = lpp.ggviolin(df, x='group', y='value', fill='group', palette='nejm')
p = lpp.ggbarplot(df, x='group', y='value', fill='group', palette='lancet')

# Or use scale functions directly
from lets_plot import ggplot, aes, geom_point
p = ggplot(df, aes(x='x', y='y', color='group')) + \
    geom_point() + \
    lpp.scale_color_pubr(palette='jama') + \
    lpp.scale_fill_pubr(palette='jama')
```

## GraphPad Prism Theme

```python
p = lpp.ggboxplot(
    df, x='group', y='value',
    ggtheme=lpp.theme_prism(
        palette='black_and_white',
        base_size=14,
        base_family='sans',
        base_fontface='bold',
        border=True
    )
)
```

## Using Native Lets-Plot Themes

All native Lets-Plot themes are available:

```python
p = lpp.ggboxplot(df, x='group', y='value', ggtheme=lpp.theme_minimal())
p = lpp.ggboxplot(df, x='group', y='value', ggtheme=lpp.theme_bw())
p = lpp.ggboxplot(df, x='group', y='value', ggtheme=lpp.theme_classic())
p = lpp.ggboxplot(df, x='group', y='value', ggtheme=lpp.theme_void())
p = lpp.ggboxplot(df, x='group', y='value', ggtheme=lpp.theme_light())
p = lpp.ggboxplot(df, x='group', y='value', ggtheme=lpp.theme_grey())
```

## Override with + Operator

```python
# Create with default theme and override
p = lpp.ggboxplot(df, x='group', y='value', fill='group') + lpp.theme_bw()
```
