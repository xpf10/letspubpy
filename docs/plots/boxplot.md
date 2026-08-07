# Boxplot

Create publication-ready box-and-whisker plots with optional jitter, dotplot, or point overlays.

## Basic Usage

```python
import pandas as pd
import numpy as np
import letspubpy as lpp

np.random.seed(42)
df = pd.DataFrame({
    'group': ['Control'] * 30 + ['Treat A'] * 30 + ['Treat B'] * 30,
    'expression': np.concatenate([
        np.random.normal(1.0, 0.4, 30),
        np.random.normal(1.8, 0.5, 30),
        np.random.normal(1.4, 0.3, 30)
    ])
})

# Basic boxplot
p = lpp.ggboxplot(df, x='group', y='expression', fill='group', palette='npg')
p.show()
```

## Adding Data Points

```python
# Add jitter points
p = lpp.ggboxplot(
    df, x='group', y='expression',
    fill='group', palette='npg',
    add='jitter'  # Options: 'jitter', 'dotplot', 'point'
)

# Custom jitter parameters
p = lpp.ggboxplot(
    df, x='group', y='expression',
    add='jitter', add_params={'width': 0.2, 'size': 2}
)
```

## Notched Boxplots

```python
p = lpp.ggboxplot(df, x='group', y='expression', notch=True)
```

## With Statistical Comparisons

```python
p = lpp.ggboxplot(df, x='group', y='expression', fill='group', add='jitter') + \
    lpp.stat_compare_means(
        comparisons=[('Control', 'Treat A'), ('Treat A', 'Treat B')],
        method='wilcoxon', color='red'
    )
```

## Custom Appearance

```python
p = lpp.ggboxplot(
    df, x='group', y='expression',
    fill='group', palette='nejm',
    title="Gene Expression",
    xlab="Treatment Group",
    ylab="Expression Level",
    show_legend=False,
    ggtheme=lpp.theme_minimal()
)
```

## API

::: letspubpy.plots.ggboxplot
    options:
        show_source: true
