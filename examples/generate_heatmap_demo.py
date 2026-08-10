import pandas as pd
import numpy as np
import letspubpy as lpp
from lets_plot import ggsave

def main():
    # 1. 构造差异基因表达矩阵示例数据
    np.random.seed(42)
    n_genes = 15
    n_samples = 10

    genes = [f'Gene_{i+1}' for i in range(n_genes)]
    samples = [f'Ctrl_{i+1}' for i in range(5)] + [f'Treat_{i+1}' for i in range(5)]

    matrix_data = np.random.randn(n_genes, n_samples)
    matrix_data[:5, :5] += 2.0    # 对照组高表达基因
    matrix_data[5:10, 5:] += 2.5  # 处理组高表达基因
    matrix_data[10:, :] += np.random.normal(0, 0.5, (5, 10))

    df = pd.DataFrame(matrix_data, index=genes, columns=samples)

    # 2. 调用 ggclustervis (即 ggheatmap + 层次聚类) 绘制热图
    p = lpp.ggclustervis(
        df,
        scale='row',           # 行标准化 (z-score)
        cluster_rows=True,     # 行层次聚类
        cluster_cols=True,     # 列层次聚类
        metric='euclidean',    # 距离度量
        method='complete',     # 聚类方法
        palette='bwr',         # 蓝白红渐变配色
        title='Publication-Ready Clustered Gene Expression Heatmap',
        xlab='Experimental Samples',
        ylab='Genes'
    )

    # 3. 保存导出的图片
    ggsave(p, 'heatmap_chart.png')
    print("热图绘制完成并已保存为 heatmap_chart.png！")

if __name__ == '__main__':
    main()
