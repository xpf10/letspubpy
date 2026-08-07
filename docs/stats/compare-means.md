# stat_compare_means

Add statistical significance brackets or labels to plots. Supports pairwise comparisons and global tests.

## Usage with + Operator

```python
import pandas as pd
import numpy as np
import letspubpy as lpp

np.random.seed(42)
df = pd.DataFrame({
    'group': ['A'] * 30 + ['B'] * 30 + ['C'] * 30,
    'value': np.concatenate([
        np.random.normal(0, 1, 30),
        np.random.normal(1.5, 1, 30),
        np.random.normal(0.5, 1, 30)
    ])
})

# Pairwise comparisons
p = lpp.ggboxplot(df, x='group', y='value', fill='group') + \
    lpp.stat_compare_means(
        comparisons=[('A', 'B'), ('B', 'C')],
        method='wilcoxon', color='red'
    )
p.show()
```

## Pairwise Tests

Supported methods for pairwise comparisons:
- `"wilcoxon"` or `"mwu"` — Mann-Whitney U / Wilcoxon rank-sum (default)
- `"t.test"` — Welch's t-test (two-sided)

```python
p = lpp.ggboxplot(df, x='group', y='value', fill='group') + \
    lpp.stat_compare_means(
        comparisons=[('A', 'B'), ('A', 'C'), ('B', 'C')],
        method='t.test'
    )
```

## Global Tests

Without `comparisons`, a global test label is added (ANOVA or Kruskal-Wallis):

```python
p = lpp.ggboxplot(df, x='group', y='value', fill='group') + \
    lpp.stat_compare_means(method='kruskal')
```

## Label Formats

```python
# p-value format (default)
p = lpp.ggboxplot(df, x='group', y='value') + \
    lpp.stat_compare_means(comparisons=[('A', 'B')], label='p.format')

# Significance asterisks
p = lpp.ggboxplot(df, x='group', y='value') + \
    lpp.stat_compare_means(comparisons=[('A', 'B')], label='p.signif')

# Custom labels (must match number of comparisons)
p = lpp.ggboxplot(df, x='group', y='value') + \
    lpp.stat_compare_means(
        comparisons=[('A', 'B'), ('B', 'C')],
        label=['Sig.', 'Not sig.']
    )
```

## Custom Significance Symbols

```python
p = lpp.ggboxplot(df, x='group', y='value') + \
    lpp.stat_compare_means(
        comparisons=[('A', 'B'), ('B', 'C')],
        label='p.signif',
        symnum_args={
            'cutpoints': [0, 0.001, 0.01, 0.05, 1],
            'symbols': ['***', '**', '*', 'ns']
        }
    )
```

## API

::: letspubpy.stats.stat_compare_means
    options:
        show_source: true

