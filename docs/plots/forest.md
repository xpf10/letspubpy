# Forest Plot (`ggforest`)

`ggforest` (aliased as `visForest`) creates publication-ready **Forest Plots** for Meta-Analyses, Cox Proportional Hazards Models, and Logistic Regressions.

---

## Key Features

- **Effect Sizes & 95% Confidence Intervals**: Displays square point estimates with horizontal confidence interval error bars.
- **Weighted Markers**: Point size scales dynamically with sample size or meta-analysis study weights (`weight="weight"`).
- **Aligned Tabular Annotations**: Automatically formats and aligns text columns for `Hazard Ratio [95% CI]` and $p$-values along the right side of the figure.
- **Reference Null Line**: Customizable dashed null-hypothesis vertical reference line (`ref_line=1.0` for ratios, `0.0` for differences).

---

## Usage Examples

### 1. Basic Forest Plot

```python
import letspubpy as lpp

# Simulate and plot meta-analysis forest plot
p = lpp.ggforest(
    ref_line=1.0,
    title="Meta-Analysis Hazard Ratios (95% CI)",
    xlab="Hazard Ratio (95% CI)",
    ylab="Studies / Clinical Trials"
)
p.show()
```

![Forest Plot](../images/forest_basic.png)

---

### 2. Custom Cox Regression Results

```python
import pandas as pd
import letspubpy as lpp

df_cox = pd.DataFrame({
    "variable": ["Age (>65 vs <=65)", "Gender (Male vs Female)", "Stage (III/IV vs I/II)", "Biomarker Positive"],
    "hr": [1.45, 0.88, 2.34, 1.78],
    "lower": [1.12, 0.65, 1.67, 1.25],
    "upper": [1.89, 1.18, 3.28, 2.54],
    "pvalue": [0.005, 0.38, 0.0001, 0.001],
    "weight": [250, 250, 180, 210]
})

p_cox = lpp.ggforest(
    df_cox,
    study="variable",
    mean="hr",
    lower="lower",
    upper="upper",
    pvalue="pvalue",
    weight="weight",
    title="Multivariate Cox Regression Forest Plot"
)
p_cox.show()
```

---

## API Reference

### ggforest

::: letspubpy.plots.ggforest
    options:
        show_source: true

### sim_forest_data

::: letspubpy.plots.sim_forest_data
    options:
        show_source: true
