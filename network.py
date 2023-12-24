import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

csv_file = "./data/packets_exfil_500k.csv" 
df = pd.read_csv(csv_file)

G = nx.DiGraph()

for _, row in df.iterrows():
    src_ip = row['src_ip']
    dst_ip = row['dst_ip']
    size = row['size']
    src_port = row['src_port']
    dst_port = row['dst_port']

    G.add_node(src_ip)
    G.add_node(dst_ip)
    G.add_edge(src_ip, dst_ip, weight=size, label=f"SRC: {src_port} // DST: {dst_port}")

pos = nx.spring_layout(G, seed=42)
labels = nx.get_edge_attributes(G, 'label')
weights = [G[u][v]['weight'] / 100 for u, v in G.edges()]

plt.figure(figsize=(12, 12))
nx.draw(G, pos, with_labels=True, node_size=100, node_color='blue', font_size=6, bbox=dict(boxstyle="round", fc="w", ec="none", pad=0.2, alpha=0.8))
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=6, bbox=dict(boxstyle="round", fc="w", ec="none", pad=0.2, alpha=0.8))
nx.draw_networkx_edges(G, pos, edgelist=G.edges(), width=weights, edge_color='#BEBEBE', alpha=0.5)
plt.tight_layout()
plt.show()
