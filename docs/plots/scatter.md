# Scatter Plot

Create scatter plots with optional regression lines, confidence ellipses, and correlation annotations.

## Basic Usage

```python
import pandas as pd
import numpy as np
import letspubpy as lpp

np.random.seed(42)
x = np.random.uniform(1, 10, 50)
y = x * 1.5 + np.random.normal(0, 1.5, 50)
df = pd.DataFrame({'x': x, 'y': y})

p = lpp.ggscatter(df, x='x', y='y', color='#3C5488')
p.show()
```

## Adding Regression Line

```python
p = lpp.ggscatter(
    df, x='x', y='y',
    color='#3C5488',
    add='reg.line', confint=True
)
```

## Grouped Scatter with Ellipses

```python
np.random.seed(42)
n = 30
df = pd.DataFrame({
    'x': np.concatenate([
        np.random.normal(0, 1, n),
        np.random.normal(3, 1, n),
        np.random.normal(-2, 1, n)
    ]),
    'y': np.concatenate([
        np.random.normal(0, 1, n),
        np.random.normal(3, 1, n),
        np.random.normal(4, 1, n)
    ]),
    'group': ['A'] * n + ['B'] * n + ['C'] * n
})

p = lpp.ggscatter(
    df, x='x', y='y',
    color='group', fill='group',
    palette='npg', size=3,
    ellipse=True, ellipse_level=0.95,
    ellipse_type='norm', ellipse_alpha=0.15
)
p.show()
```

## Adding Rug Plot

```python
p = lpp.ggscatter(df, x='x', y='y', color='#3C5488', rug=True)
```

## With Correlation Annotation

```python
p = lpp.ggscatter(df, x='x', y='y', color='#3C5488') + \
    lpp.stat_cor(method='pearson', size=12)
```

## Full Feature Set

```python
p = lpp.ggscatter(
    df, x='x', y='y',
    color='group', fill='group',
    palette='npg', shape=19, size=3,
    add='reg.line', confint=True, confint_level=0.95,
    ellipse=True, ellipse_level=0.95, ellipse_type='norm', ellipse_alpha=0.15,
    rug=True, rug_size=0.5,
    cor=True, cor_method='pearson', cor_size=12,
    label='group', label_size=4,
    title="Scatter Plot", xlab="X Axis", ylab="Y Axis",
    aspect_ratio=1
)
```

## API

::: letspubpy.plots.ggscatter
    options:
        show_source: true

