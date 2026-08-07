# Getting Started

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Install from PyPI

```bash
pip install letspubpy
```

### Install from Source

```bash
git clone https://github.com/xpf10/letspubpy.git
cd letspubpy
pip install -e .
```

### Install with uv (recommended)

```bash
uv add letspubpy
```

---

## Your First Plot

Create a simple boxplot with publication-ready styling:

```python
import pandas as pd
import numpy as np
import letspubpy as lpp

# Create sample data
np.random.seed(42)
df = pd.DataFrame({
    'group': ['A'] * 20 + ['B'] * 20 + ['C'] * 20,
    'value': np.concatenate([
        np.random.normal(0, 1, 20),
        np.random.normal(1.5, 1, 20),
        np.random.normal(0.5, 1, 20)
    ])
})

# Create a publication-ready boxplot
p = lpp.ggboxplot(
    df, x='group', y='value',
    fill='group', palette='npg',
    add='jitter',
    title="My First letspubpy Plot"
)

# Display the plot
p.show()
```

---

## Common Plot Types

| Function | Description |
|----------|-------------|
| `ggboxplot()` | Box-and-whisker plots |
| `ggviolin()` | Violin plots with density |
| `ggbarplot()` | Bar charts with error bars |
| `ggline()` | Line plots with error bars |
| `ggscatter()` | Scatter plots with regression |
| `gghistogram()` | Histograms |
| `ggdensity()` | Density curves |
| `ggpie()` / `ggdonutchart()` | Pie and donut charts |
| `ggqqplot()` | Q-Q normality plots |
| `ggecdf()` | Empirical CDF plots |
| `ggcorr()` | Correlation heatmaps |

---

## Adding Statistics

Use the `+` operator to add statistical annotations:

```python
# Add pairwise comparisons
p = lpp.ggboxplot(df, x='group', y='value', fill='group') + lpp.stat_compare_means(
    comparisons=[('A', 'B'), ('B', 'C')],
    method='wilcoxon'
)

# Add correlation to scatter plots
p = lpp.ggscatter(df, x='x', y='y', color='group') + lpp.stat_cor(
    method='pearson', size=12
)
```

---

## Next Steps

- Browse [plot examples](examples.md) for detailed usage
- Check the [API Reference](api-reference.md) for all parameters
- Explore [themes and palettes](themes-and-palettes.md) for customization
