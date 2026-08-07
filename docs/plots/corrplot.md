# Correlation Heatmap

Create correlation heatmaps to visualize pairwise correlations between variables.

## Basic Usage

```python
import pandas as pd
import numpy as np
import letspubpy as lpp

np.random.seed(42)
df = pd.DataFrame({
    'x': np.random.normal(0, 1, 50),
    'y': np.random.normal(0, 1, 50),
    'z': np.random.normal(0, 1, 50),
})

p = lpp.ggcorr(df, method='pearson')
p.show()
```

## Correlation Methods

```python
# Pearson correlation (default)
p = lpp.ggcorr(df, method='pearson')

# Spearman rank correlation
p = lpp.ggcorr(df, method='spearman')

# Kendall tau correlation
p = lpp.ggcorr(df, method='kendall')
```

## Showing P-value Symbols

```python
p = lpp.ggcorr(
    df, method='pearson',
    p_low='*',      # Symbol for p < 0.05
    p_high='ns'     # Symbol for p >= 0.05
)
```

## Custom Precision

```python
p = lpp.ggcorr(df, method='pearson', digits=3)
```

## API

::: letspubpy.plots.ggcorr
    options:
        show_source: true

