import pandas as pd
import numpy as np
import letspubpy as lpp
from lets_plot import ggsave

def main():
    # 1. 模拟时间序列/多条件基因表达矩阵 (24个基因 x 6个时间点)
    np.random.seed(42)
    genes = [f'Gene_{i+1:02d}' for i in range(24)]
    timepoints = ['0h', '2h', '6h', '12h', '24h', '48h']

    t = np.linspace(0, 2 * np.pi, 6)
    p1 = np.sin(t)        # 早期升高
    p2 = np.cos(t)        # 晚期升高
    p3 = np.exp(-t)       # 持续下降
    p4 = 1 - np.exp(-t)   # 持续上升

    data = []
    for i in range(24):
        if i < 6: pattern = p1
        elif i < 12: pattern = p2
        elif i < 18: pattern = p3
        else: pattern = p4
        data.append(pattern + np.random.normal(0, 0.2, 6))

    df_mat = pd.DataFrame(data, index=genes, columns=timepoints)

    # 2. 调用 ClusterGVis 风格的 visCluster 双视图 API
    # plot_type='both': 左侧分块热图 + 右侧各 Cluster 表达趋势折线图
    p = lpp.visCluster(
        df_mat,
        n_clusters=4,           # 划分为 4 个 Cluster 模块
        scale='row',            # 行 Z-score 标准化
        plot_type='both',       # 同时展示 热图 + 趋势线
        palette='bwr',          # 热图配色（蓝白红）
        cluster_palette='npg',  # 趋势折线图配色（Nature）
        title='ClusterGVis Expression Dynamics',
        xlab='Time Point'
    )

    # 3. 保存导出
    ggsave(p, 'chart.png')
    print("ClusterGVis 风格双视图热图绘制完成！")

if __name__ == '__main__':
    main()
