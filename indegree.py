import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import zscore

def visualize_network_graph(file_path, port):
    df = pd.read_csv(file_path)
    filtered_df = df[(df['src_port'] == port) | (df['dst_port'] == port)]
    G = nx.DiGraph()

    for _, row in filtered_df.iterrows():
        G.add_edge(row['src_mac'], row['dst_mac'], weight=row['size'])

    weighted_in_degree = G.in_degree(weight='weight')
    in_degree_values = [degree for _, degree in weighted_in_degree]
    z_scores = zscore(in_degree_values)

    node_color = []
    node_shape = []
    for node, degree in weighted_in_degree:
        z = z_scores[list(G.nodes).index(node)]
        node_color.append('gray' if z <= 1.645 else 'blue')  # Blue for normal, red for high z-score
        node_shape.append('o' if z <= 1.645 else 'D')  # Circle for normal, diamond for high z-score

    fig = plt.figure(num=1, figsize=(8, 8))
    fig.canvas.manager.window.wm_geometry("+50+50")

    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=150)

    for shape in set(node_shape):
        nodes_of_current_shape = [s for s, shape_ in zip(G.nodes, node_shape) if shape_ == shape]
        colors_of_current_shape = [c for c, shape_ in zip(node_color, node_shape) if shape_ == shape]
        nx.draw_networkx_nodes(G, pos, node_size=100, 
                            nodelist=nodes_of_current_shape, 
                            node_color=colors_of_current_shape, node_shape=shape)
    
    z_scores_dict = {node: z for node, z in zip(G.nodes, z_scores)}
    labels = {node: f'{node}\n{z_scores_dict[node]:.2f}' for node in G.nodes()}
    nx.draw_networkx_edges(G, pos, width=0.25, edge_color='#BEBEBE')
    label_pos = {node: (pos[node][0], pos[node][1]+0.05) for node in G.nodes()}
    nx.draw_networkx_labels(G, label_pos, labels=labels, font_size=8, font_color='black', bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', boxstyle='round,pad=0.25'))
    plt.title(f'Network Graph for Port: {port}', fontsize=8)
    plt.tight_layout()
    plt.show()

file_path = './data/packets_chum.csv'
port = 63458
visualize_network_graph(file_path, port)
