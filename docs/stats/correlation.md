# stat_cor

Add correlation coefficient annotations to scatter plots.

## Usage with + Operator

```python
import pandas as pd
import numpy as np
import letspubpy as lpp

np.random.seed(42)
x = np.random.uniform(1, 10, 50)
y = x * 1.5 + np.random.normal(0, 1.5, 50)
df = pd.DataFrame({'x': x, 'y': y})

p = lpp.ggscatter(df, x='x', y='y') + \
    lpp.stat_cor(method='pearson', size=12)
p.show()
```

## Correlation Methods

```python
# Pearson correlation (default)
p = lpp.ggscatter(df, x='x', y='y') + lpp.stat_cor(method='pearson')

# Spearman rank correlation
p = lpp.ggscatter(df, x='x', y='y') + lpp.stat_cor(method='spearman')

# Kendall tau correlation
p = lpp.ggscatter(df, x='x', y='y') + lpp.stat_cor(method='kendall')
```

## Label Format Options

```python
# R and p-value (default)
p = lpp.ggscatter(df, x='x', y='y') + lpp.stat_cor(label='R, p')

# R and R-squared
p = lpp.ggscatter(df, x='x', y='y') + lpp.stat_cor(label='R, R2')

# R, R-squared, and p
p = lpp.ggscatter(df, x='x', y='y') + lpp.stat_cor(label='R, R2, p')

# R only
p = lpp.ggscatter(df, x='x', y='y') + lpp.stat_cor(label='R')
```

## Standalone Usage

```python
# Can also be used as a standalone function
text_layer = lpp.stat_cor(
    data=df, x='x', y='y',
    method='pearson', size=12
)
```

## API

::: letspubpy.stats.stat_cor
    options:
        show_source: true

