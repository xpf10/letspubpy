# Histogram

Create histograms showing the distribution of a variable.

## Basic Usage

```python
import pandas as pd
import numpy as np
import letspubpy as lpp

np.random.seed(42)
df = pd.DataFrame({
    'value': np.random.normal(0, 1, 200)
})

p = lpp.gghistogram(df, x='value', fill='#3C5488', bins=30)
p.show()
```

## Grouped Histogram

```python
np.random.seed(42)
df = pd.DataFrame({
    'value': np.concatenate([
        np.random.normal(0, 1, 100),
        np.random.normal(2, 1, 100)
    ]),
    'group': ['A'] * 100 + ['B'] * 100
})

p = lpp.gghistogram(
    df, x='value',
    fill='group', palette='npg',
    bins=30, position='identity'
)
```

## API

::: letspubpy.plots.gghistogram
    options:
        show_source: true

