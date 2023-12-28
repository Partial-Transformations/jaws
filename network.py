import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

csv_file = "./data/packets.csv"
df = pd.read_csv(csv_file)
G = nx.MultiDiGraph()
edge_labels = {}

for _, row in df.iterrows():
    src_mac = row['src_mac']
    dst_mac = row['dst_mac']
    G.add_node(src_mac)
    G.add_node(dst_mac)
    G.add_edge(src_mac, dst_mac)

degree_centrality = nx.degree_centrality(G)
pos = nx.spring_layout(G, seed=42, iterations=200, k=0.75)
plt.figure(figsize=(12, 12))
nx.draw(G, pos, with_labels=True, node_size=100, node_color='blue', font_size=6, bbox=dict(boxstyle="round", fc="w", ec="none", pad=0.2, alpha=0.8))

for node, degree_centrality_score in degree_centrality.items():
    label_text = f"{node}\nDegree: {degree_centrality_score:.3f}"
    plt.text(pos[node][0], pos[node][1], label_text, fontsize=6, horizontalalignment='center', verticalalignment='center', bbox=dict(boxstyle="round", fc="w", ec="none", pad=0.2, alpha=0.8))

plt.show()
