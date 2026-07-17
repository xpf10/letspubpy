# letspubpy 📊

A publication-ready plotting library that wraps **Lets-Plot** in Python, mimicking the design and high-level simplicity of R's famous **ggpubr** package.

`letspubpy` simplifies creation of journal-quality scientific plots (such as box plots, violin plots, and bar charts) with automated statistical comparisons, publication color palettes, and easy grid arrangements, while maintaining full compatibility with the grammar of graphics under Lets-Plot.

---

## Key Features

- **High-Level Plots**: Build complex boxplots, violin plots, dotplots, line plots, and pie charts with simple, intuitive functions (`ggboxplot`, `ggviolin`, `ggbarplot`, `ggscatter`, `ggpie`, etc.).
- **Automatic Statistics (`+ stat_compare_means`)**: Easily calculate and annotate plots with statistical test brackets (Welch's t-test, Mann-Whitney U / Wilcoxon, ANOVA, Kruskal-Wallis) using Python's `scipy.stats`.
- **Journal Color Palettes**: Directly apply color schemes matching top journals like Nature (`npg`), Science (`aaas`), NEJM (`nejm`), JAMA (`jama`), Lancet (`lancet`), and JCO (`jco`).
- **Flexible Grid Layouts (`ggarrange`)**: Combine multiple plots into a clean subplot panel with a unified legend.
- **Fluent Integration**: Seamlessly extends Lets-Plot; you can still use the standard `+` operator to add native geoms, scales, facets, and labels.

---

## Installation

You can install `letspubpy` in your project with `uv` or `pip`:

```bash
# Install directly from the local folder
pip install .

# Or with uv
uv add .
```

### Install from GitHub Releases
You can download the pre-built wheel (`.whl`) or source distribution from the [GitHub Releases Page](https://github.com/xpf10/letspubpy/releases) and install it directly:

```bash
# Install from the downloaded wheel
pip install letspubpy-0.1.0-py3-none-any.whl

# Or install directly via the release download URL
pip install https://github.com/xpf10/letspubpy/releases/download/v0.1.0/letspubpy-0.1.0-py3-none-any.whl
```

---

## Quick Start & Examples

Here is a quick overview of how to build publication-grade plots in Python:

### 1. High-Level Boxplots with Statistical Comparisons

```python
import pandas as pd
import numpy as np
import letspubpy as lpp

# Create sample dataset
np.random.seed(42)
df = pd.DataFrame({
    'group': ['Control'] * 30 + ['Treat A'] * 30 + ['Treat B'] * 30,
    'expression': np.concatenate([
        np.random.normal(loc=1.0, scale=0.4, size=30),
        np.random.normal(loc=1.8, scale=0.5, size=30),
        np.random.normal(loc=1.4, scale=0.3, size=30)
    ])
})

# Create boxplot with individual jitter points, publication colors, and Wilcoxon tests
p = lpp.ggboxplot(
    df, x='group', y='expression',
    fill='group', palette='npg', 
    add='jitter', title="Gene Expression Analysis"
) + lpp.stat_compare_means(
    comparisons=[('Control', 'Treat A'), ('Treat A', 'Treat B'), ('Control', 'Treat B')],
    method='wilcoxon',
    color='red'
)

# Render or save
p.show()
```

![Boxplot Example](images/boxplot_example.svg)

### 2. Violin Plots with Inner Boxplots

```python
# Create violin plot with an embedded boxplot and NEJM color scheme
p_violin = lpp.ggviolin(
    df, x='group', y='expression',
    fill='group', palette='nejm',
    add='boxplot', title="Expression Density"
)
p_violin.show()
```

![Violin Example](images/violin_example.svg)

### 3. Combining Plots into a Layout (`ggarrange`)

```python
# Create a scatter plot with a linear regression fit
x_val = np.random.uniform(1, 10, size=50)
y_val = x_val * 1.5 + np.random.normal(0, 1.2, size=50)
df_scatter = pd.DataFrame({'x': x_val, 'y': y_val})

p_scatter = lpp.ggscatter(
    df_scatter, x='x', y='y',
    color='#3C5488', add='reg.line',
    title="Correlation Plot"
)

# Combine the box plot and scatter plot in a 1-row, 2-column grid
grid = lpp.ggarrange(
    p, p_scatter,
    ncol=2, common_legend=True, legend='bottom'
)
grid.show()
```

![Arranged Grid Example](images/arrange_example.svg)

### 4. Customizing Themes & Fonts

You can use `letspubpy`'s built-in `theme_pubr()` or any of Lets-Plot's standard themes (like `theme_minimal()`, `theme_bw()`, `theme_classic()`, `theme_void()`, etc.) in two ways:

#### A. Pass the theme to the plotting function directly:
```python
# Pass theme_minimal() using the ggtheme parameter
p_minimal = lpp.ggboxplot(
    df, x='group', y='expression',
    fill='group', palette='npg', 
    ggtheme=lpp.theme_minimal()
)
p_minimal.show()
```

#### B. Override using the `+` operator:
```python
# Create with default theme_pubr() and override using the standard + operator
p_bw = lpp.ggboxplot(df, x='group', y='expression', fill='group') + lpp.theme_bw()
p_bw.show()
```

---

## API Documentation

### Plotting Functions
All plotting functions support standard parameters (`color`, `fill`, `palette`, `title`, `xlab`, `ylab`, `show_legend`, `ggtheme`):
- `ggboxplot(data, x, y, notch=False, add="none", ...)`: Create a boxplot. `add` can be `"jitter"`, `"dotplot"`, or `"point"`.
- `ggviolin(data, x, y, draw_quantiles=None, add="none", ...)`: Create a violin plot. `add` can be `"boxplot"`, `"jitter"`, or `"dotplot"`.
- `ggbarplot(data, x, y=None, add="none", ...)`: Create a bar chart showing counts (if `y=None`) or group means (if `y` is provided). `add` can be `"mean_se"` or `"mean_sd"` to automatically add error bars.
- `ggline(data, x, y, add="none", ...)`: Create a line plot of group means. `add` can be `"mean_se"` or `"mean_sd"`.
- `ggscatter(data, x, y, add="none", ...)`: Create a scatter plot. `add` can be `"reg.line"` to draw a linear regression trend.
- `gghistogram(data, x, y="..count..", bins=30, ...)`: Create a histogram.
- `ggdensity(data, x, y="..density..", ...)`: Create a density curve.
- `ggpie(data, x, label, fill=None, hole=0, ...)`: Create a pie chart.
- `ggdonutchart(data, x, label, fill=None, hole=0.4, ...)`: Create a donut chart.

### Themes & Color Palettes
- `theme_pubr(base_size=12, base_family=None, legend="top", border=False)`: Custom clean publication-ready theme.
- `scale_color_pubr(palette="npg")` & `scale_fill_pubr(palette="npg")`: Use journal color palettes (`npg`, `aaas`, `nejm`, `jama`, `jco`, `lancet`, `locuszoom`, `simpsons`, `tron`).

### Statistics & Layouts
- `stat_compare_means(comparisons=None, method="wilcoxon", paired=False, label="p.format", size=None, symnum_args=None, ...)`: Add statistical significance brackets (if `comparisons` is provided) or a global label (ANOVA/Kruskal-Wallis) to the plot.
  - `size`: Configure the font size of the significance labels.
  - `symnum_args`: Customize significance thresholds/symbols via a dict, e.g. `{"cutpoints": [0, 0.01, 1], "symbols": ["significant", "ns"]}`.
  - `label`: Can be `"p.format"`, `"p.signif"`, or a list of custom string labels matching the comparisons (e.g. `["Group A vs B", "Group B vs C"]`).
- `ggarrange(*plots, ncol=None, nrow=None, common_legend=False, legend="bottom")`: Combine multiple plots on a grid.

---

## License

This project is licensed under the MIT License.
