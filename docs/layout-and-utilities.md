# Layout & Utilities

Combine multiple plots and modify plot appearance with utility functions.

## ggarrange — Combine Plots

Create multi-panel figures with a shared legend.

```python
import pandas as pd
import numpy as np
import letspubpy as lpp

np.random.seed(42)
df = pd.DataFrame({
    'group': ['A'] * 30 + ['B'] * 30,
    'value': np.concatenate([
        np.random.normal(0, 1, 30),
        np.random.normal(1.5, 1, 30)
    ]),
    'score': np.concatenate([
        np.random.normal(50, 10, 30),
        np.random.normal(60, 10, 30)
    ])
})

# Create individual plots
p1 = lpp.ggboxplot(df, x='group', y='value', fill='group', palette='npg')
p2 = lpp.ggviolin(df, x='group', y='score', fill='group', palette='npg')

# Combine in a 1-row, 2-column grid
grid = lpp.ggarrange(p1, p2, ncol=2, common_legend=True, legend='bottom')
grid.show()
```

### Grid Options

```python
# 2 rows, 1 column
grid = lpp.ggarrange(p1, p2, nrow=2)

# 2x2 grid
grid = lpp.ggarrange(p1, p2, p3, p4, ncol=2, nrow=2)

# Shared legend
grid = lpp.ggarrange(p1, p2, common_legend=True, legend='right')

# Remove individual legends
grid = lpp.ggarrange(
    lpp.rremove(p1, 'legend'),
    lpp.rremove(p2, 'legend'),
    ncol=2
)
```

## rremove — Remove Plot Elements

```python
# Remove title
p = lpp.rremove(plot, 'title')

# Remove axis labels
p = lpp.rremove(plot, 'xlab')
p = lpp.rremove(plot, 'ylab')
p = lpp.rremove(plot, 'axis')  # Remove both axes

# Remove axis tick labels
p = lpp.rremove(plot, 'x.text')
p = lpp.rremove(plot, 'y.text')

# Remove axis lines
p = lpp.rremove(plot, 'x.axis')
p = lpp.rremove(plot, 'y.axis')

# Remove legend
p = lpp.rremove(plot, 'legend')

# Remove grid
p = lpp.rremove(plot, 'grid')

# Chain multiple removals
p = lpp.rremove(lpp.rremove(plot, 'title'), 'xlab')
```

## ggpar — Customize Plot Appearance

```python
# Change labels
p = lpp.ggpar(plot, title="New Title", xlab="New X", ylab="New Y")

# Change palette
p = lpp.ggpar(plot, palette='nejm')

# Change legend position
p = lpp.ggpar(plot, legend='top')
p = lpp.ggpar(plot, legend='none')  # Hide legend

# Set base font size
p = lpp.ggpar(plot, font_size=14)
```

## API

::: letspubpy.arrange.ggarrange
    options:
        show_source: true


::: letspubpy.plots.rremove
    options:
        show_source: true


::: letspubpy.plots.ggpar
    options:
        show_source: true

