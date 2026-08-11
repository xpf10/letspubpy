import letspubpy as lpp
from lets_plot import ggsave

# 1. Generate synthetic pathway enrichment data
df_enrich = lpp.sim_enrichment_data(n_terms=12)

# 2. Lollipop Chart (棒棒糖图)
p_lollipop = lpp.visEnrichLollipop(df_enrich, top_n=10, title="GO/KEGG Enrichment Lollipop Chart")
ggsave(p_lollipop, "enrichment_lollipop_demo.png")

# 3. Concept Network Chart (Network图 / cnetplot)
p_network = lpp.visEnrichNetwork(df_enrich, top_n=5, title="Pathway-Gene Concept Network (cnetplot)")
ggsave(p_network, "enrichment_network_demo.png")

print("Both Enrichment Lollipop and Network demo charts saved successfully!")
