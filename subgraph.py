import pandas as pd
import networkx as nx
from scipy.stats import zscore

def compute_out_degree(df, port):
    G = nx.DiGraph()
    filtered_df = df[(df['src_port'] == port) | (df['dst_port'] == port)]

    for _, row in filtered_df.iterrows():
        G.add_edge(row['src_mac'], row['dst_mac'], weight=row['size'])

    weighted_out_degree = G.out_degree(weight='weight')
    node_out, degree_out = max(weighted_out_degree, key=lambda x: x[1], default=(None, None))
    return node_out, degree_out

def compute_in_degree(df, port):
    G = nx.DiGraph()
    filtered_df = df[(df['src_port'] == port) | (df['dst_port'] == port)]

    for _, row in filtered_df.iterrows():
        G.add_edge(row['src_mac'], row['dst_mac'], weight=row['size'])

    weighted_in_degree = G.in_degree(weight='weight')
    in_degree_values = [degree for _, degree in weighted_in_degree]
    z_scores = zscore(in_degree_values)
    significant_nodes = [(node, z) for (node, _), z in zip(weighted_in_degree, z_scores)]
    
    if significant_nodes:
        node_in, z_in_degree = max(significant_nodes, key=lambda x: x[1], default=(None, None))
    else:
        node_in, z_in_degree = None, None

    return node_in, z_in_degree

def analyze_network_data(file_path, output_file):
    df = pd.read_csv(file_path)
    unique_ports = set(df['src_port']).union(set(df['dst_port']))
    results = []

    for port in unique_ports:
        node_out, degree_out = compute_out_degree(df, port)
        node_in, z_in_degree = compute_in_degree(df, port)

        results.append({
            'port': port, 
            'dst_mac_out': node_out, 
            'weighted_outdegree': degree_out, 
            'dst_mac_zin': node_in, 
            'z_indegree': z_in_degree
        })

    results_df = pd.DataFrame(results)
    results_df.sort_values(by='z_indegree', ascending=False, inplace=True)
    results_df.to_csv(output_file, index=False)

file_path = './data/packets_chum.csv'
output_file = './data/subgraph.csv'
analyze_network_data(file_path, output_file)
