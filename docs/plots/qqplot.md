# Q-Q Plot

Create Q-Q (quantile-quantile) plots to assess normality of a distribution.

## Basic Usage

```python
import pandas as pd
import numpy as np
import letspubpy as lpp

np.random.seed(42)
df = pd.DataFrame({
    'value': np.random.normal(0, 1, 200)
})

p = lpp.ggqqplot(df, x='value')
p.show()
```

## Adding Reference Line

```python
p = lpp.ggqqplot(df, x='value', add='qqline')
```

![Q-Q Plot Example](../images/qqplot_basic.png)

## Grouped Q-Q Plot

```python
np.random.seed(42)
df = pd.DataFrame({
    'value': np.concatenate([
        np.random.normal(0, 1, 100),
        np.random.normal(2, 1, 100)
    ]),
    'group': ['A'] * 100 + ['B'] * 100
})

p = lpp.ggqqplot(
    df, x='value',
    color='group', fill='group',
    add='qqline', palette='npg'
)
```

## API

::: letspubpy.plots.ggqqplot
    options:
        show_source: true

