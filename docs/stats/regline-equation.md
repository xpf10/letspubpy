# stat_regline_equation

Add linear regression equation annotations to scatter plots.

## Usage with + Operator

```python
import pandas as pd
import numpy as np
import letspubpy as lpp

np.random.seed(42)
x = np.random.uniform(1, 10, 50)
y = x * 1.5 + np.random.normal(0, 1.5, 50)
df = pd.DataFrame({'x': x, 'y': y})

# Add regression line and equation
p = lpp.ggscatter(df, x='x', y='y', add='reg.line') + \
    lpp.stat_regline_equation(label='equation', size=10)
p.show()
```

## Label Formats

```python
# Equation only (default): y = bx + a
p = lpp.ggscatter(df, x='x', y='y', add='reg.line') + \
    lpp.stat_regline_equation(label='equation')

# Equation with p-value
p = lpp.ggscatter(df, x='x', y='y', add='reg.line') + \
    lpp.stat_regline_equation(label='eqp')

# R-squared only
p = lpp.ggscatter(df, x='x', y='y', add='reg.line') + \
    lpp.stat_regline_equation(label='R2')

# Equation with R-squared
p = lpp.ggscatter(df, x='x', y='y', add='reg.line') + \
    lpp.stat_regline_equation(label='eqR2')

# Equation with p-value and R-squared
p = lpp.ggscatter(df, x='x', y='y', add='reg.line') + \
    lpp.stat_regline_equation(label='eqpR2')
```

## Standalone Usage

```python
text_layer = lpp.stat_regline_equation(
    data=df, x='x', y='y',
    label='eqR2', size=10
)
```

## API

::: letspubpy.stats.stat_regline_equation
    options:
        show_source: true

