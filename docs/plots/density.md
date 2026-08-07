# Density Plot

Create density curves showing the probability density distribution.

## Basic Usage

```python
import pandas as pd
import numpy as np
import letspubpy as lpp

np.random.seed(42)
df = pd.DataFrame({
    'value': np.random.normal(0, 1, 200)
})

p = lpp.ggdensity(df, x='value', fill='#3C5488')
p.show()
```

## Grouped Density

```python
np.random.seed(42)
df = pd.DataFrame({
    'value': np.concatenate([
        np.random.normal(0, 1, 100),
        np.random.normal(2, 1, 100)
    ]),
    'group': ['A'] * 100 + ['B'] * 100
})

p = lpp.ggdensity(
    df, x='value',
    fill='group', palette='npg',
    alpha=0.5
)
```

## API

::: letspubpy.plots.ggdensity
    options:
        show_source: true

