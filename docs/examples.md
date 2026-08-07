# Examples

Complete examples demonstrating letspubpy's capabilities.

## Example 1: Boxplot with Statistical Comparisons

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

p = lpp.ggboxplot(
    df, x='group', y='expression',
    fill='group', palette='npg',
    add='jitter', title="Gene Expression Analysis"
) + lpp.stat_compare_means(
    comparisons=[('Control', 'Treat A'), ('Treat A', 'Treat B')],
    method='wilcoxon', color='red'
)
p.show()
```

## Example 2: Violin Plot with Embedded Boxplot

```python
p = lpp.ggviolin(
    df, x='group', y='expression',
    fill='group', palette='nejm',
    add='boxplot', title="Expression Density"
)
p.show()
```

## Example 3: Scatter Plot with Regression and Correlation

```python
np.random.seed(42)
x = np.random.uniform(1, 10, 50)
y = x * 1.5 + np.random.normal(0, 1.5, 50)
df_scatter = pd.DataFrame({'x': x, 'y': y})

p = lpp.ggscatter(
    df_scatter, x='x', y='y',
    color='#3C5488',
    add='reg.line', confint=True,
    title="Correlation Plot"
) + lpp.stat_cor(method='pearson', size=12)
p.show()
```

## Example 4: Multi-panel Figure

```python
# Create individual plots
p_box = lpp.ggboxplot(df, x='group', y='expression',
                      fill='group', palette='npg', add='jitter')
p_violin = lpp.ggviolin(df, x='group', y='expression',
                        fill='group', palette='npg', add='boxplot')
p_hist = lpp.gghistogram(df, x='expression', fill='#3C5488', bins=20)
p_scatter = lpp.ggscatter(df_scatter, x='x', y='y',
                          color='#3C5488', add='reg.line')

# Combine in a 2x2 grid
grid = lpp.ggarrange(
    p_box, p_violin, p_hist, p_scatter,
    ncol=2, nrow=2
)
grid.show()
```

## Example 5: PCA Clustering with Confidence Ellipses

```python
np.random.seed(42)
n = 30
X = np.vstack([
    np.random.multivariate_normal([0, 0], [[1, 0.3], [0.3, 1]], size=n),
    np.random.multivariate_normal([3, 3], [[1, -0.2], [-0.2, 1]], size=n),
    np.random.multivariate_normal([-2, 4], [[1, 0.1], [0.1, 1]], size=n),
])
df_pca = pd.DataFrame(X, columns=['PC1', 'PC2'])
df_pca['group'] = ['A'] * n + ['B'] * n + ['C'] * n

p = lpp.ggscatter(
    df_pca, x='PC1', y='PC2',
    color='group', fill='group',
    palette='npg', size=3,
    ellipse=True, ellipse_level=0.95, ellipse_type='norm',
    ellipse_alpha=0.15,
    rug=True, cor=True, cor_method='pearson', cor_size=12,
    title="PCA Clustering with 95% Confidence Ellipses"
)
p.show()
```

## Example 6: Correlation Heatmap

```python
np.random.seed(42)
df_corr = pd.DataFrame({
    'height': np.random.normal(170, 10, 100),
    'weight': np.random.normal(70, 15, 100),
    'age': np.random.normal(30, 5, 100),
    'score': np.random.normal(80, 10, 100),
})

p = lpp.ggcorr(
    df_corr, method='pearson',
    p_low='*', p_high='ns',
    title="Correlation Matrix"
)
p.show()
```

## Example 7: Customizing with rremove and ggpar

```python
p = lpp.ggboxplot(df, x='group', y='expression',
                  fill='group', palette='npg',
                  title="My Plot", xlab="Groups", ylab="Values")

# Remove title and x-axis label
p = lpp.rremove(p, 'title')
p = lpp.rremove(p, 'xlab')

# Or customize with ggpar
p = lpp.ggpar(p, title="New Title", palette='nejm', legend='top')
```
