import pandas as pd
import numpy as np
import letspubpy as lpp
from lets_plot import ggsave

def main():
    # 1. 构造实验示例数据
    np.random.seed(42)
    n_per_group = 15
    groups = ['Control', 'Low Dose', 'High Dose']
    timepoints = ['24h', '48h']

    data = []
    for g in groups:
        for t in timepoints:
            base_val = 10 if g == 'Control' else (18 if g == 'Low Dose' else 28)
            time_mult = 1.0 if t == '24h' else 1.3
            values = np.random.normal(loc=base_val * time_mult, scale=2.5, size=n_per_group)
            for v in values:
                data.append({'Group': g, 'Timepoint': t, 'Expression': max(0, v)})

    df = pd.DataFrame(data)

    # 2. 绘制 NPG 期刊配色分组柱状图（带 SE 标准误 Error Bar）
    p_grouped = lpp.ggbarplot(
        df, x='Group', y='Expression',
        fill='Timepoint', palette='npg',
        add='mean_se',
        title='Gene Expression Analysis across Timepoints',
        xlab='Experimental Group',
        ylab='Relative Expression Level (Mean ± SE)'
    )

    # 3. 绘制 GraphPad Prism 风格柱状图
    p_prism = lpp.ggbarplot(
        df[df['Timepoint'] == '48h'], x='Group', y='Expression',
        fill='Group', palette='npg',
        add='mean_sd',
        title='48h Response (GraphPad Prism Style)',
        xlab='Group',
        ylab='Expression Level (Mean ± SD)',
        ggtheme=lpp.theme_prism(border=True)
    )

    # 4. 组合多图组合
    p_grid = lpp.ggarrange(p_grouped, p_prism, ncol=2, common_legend=False)

    # 保存结果
    ggsave(p_grouped, 'barplot_grouped.png')
    ggsave(p_prism, 'barplot_prism.png')
    ggsave(p_grid, 'barplot_grid.png')
    print("柱状图绘制成功并已导出为图片！")

if __name__ == '__main__':
    main()
