import letspubpy as lpp
from lets_plot import ggsave

# 1. Simulate GSEA prerank data (or pass real gseapy / blitzgsea results)
res_data, term, rnk = lpp.sim_gsea_data(n_genes=120, n_hits=15, nes=1.92, pval=0.0001, fdr=0.001, term="KEGG_CELL_CYCLE")

# 2. Generate GSEA enrichment plot
p_gsea = lpp.visGSEA(res_data, term, rnk=rnk)

# 3. Save plot
ggsave(p_gsea, "gsea_demo.png")
print("GSEA demo plot saved successfully to gsea_demo.png!")
