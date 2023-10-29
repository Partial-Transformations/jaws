import math
import json
import igraph as ig

min_size = 25
max_size = 50

def hits_algorithm(graph, max_iter=100, tol=1e-06):
    vertices_count = len(graph.vs)
    hub_score = [1] * vertices_count
    authority_score = [1] * vertices_count

    for i in range(max_iter):
        # Update authority scores
        new_authority_score = [0] * vertices_count
        for edge in graph.es:
            new_authority_score[edge.target] += hub_score[edge.source]
        
        # Update hub scores
        new_hub_score = [0] * vertices_count
        for edge in graph.es:
            new_hub_score[edge.source] += new_authority_score[edge.target]
        
        # Normalize
        auth_sum = sum(new_authority_score)
        hub_sum = sum(new_hub_score)
        
        new_authority_score = [x / auth_sum for x in new_authority_score]
        new_hub_score = [x / hub_sum for x in new_hub_score]

        # Check for convergence
        if all(abs(new_hub_score[i] - hub_score[i]) < tol for i in range(vertices_count)) and \
           all(abs(new_authority_score[i] - authority_score[i]) < tol for i in range(vertices_count)):
            break
        
        hub_score, authority_score = new_hub_score, new_authority_score

    return hub_score, authority_score

# Read JSON file containing packet data
with open("packets.json", "r") as f:
    packets = json.load(f)

# Initialize igraph object
g = ig.Graph(directed=True)

# Add vertices and edges to the graph
ip_addresses = set()
for packet in packets:
    src_ip = packet["src_ip"]
    dst_ip = packet["dst_ip"]

    ip_addresses.add(src_ip)
    ip_addresses.add(dst_ip)

g.add_vertices(list(ip_addresses))

for packet in packets:
    src_ip = packet["src_ip"]
    dst_ip = packet["dst_ip"]
    
    g.add_edges([(src_ip, dst_ip)])

# Assign attributes to vertices and edges if necessary
for packet in packets:
    edge_id = g.get_eid(packet["src_ip"], packet["dst_ip"])
    g.es[edge_id]["src_port"] = packet["src_port"]
    g.es[edge_id]["dst_port"] = packet["dst_port"]
    g.es[edge_id]["timestamp"] = packet["timestamp"]

# Calculate hub and authority scores manually
hub_score, authority_score = hits_algorithm(g)

# Normalize hub scores to [0, 1] range
min_hub_score = min(hub_score)
max_hub_score = max(hub_score)
normalized_hub_score = [(score - min_hub_score) / (max_hub_score - min_hub_score) for score in hub_score]

# Assign these scores to the graph's vertices
g.vs["hub_score"] = normalized_hub_score
g.vs["authority_score"] = authority_score

# Calculate betweenness centrality
g.vs["betweenness"] = g.betweenness(directed=True)

"""
# Create clusters based on hub score
median_hub_score = sorted(hub_score)[len(hub_score) // 2]
clusters = ["High Hub Score" if score >= median_hub_score else "Low Hub Score" for score in hub_score]
g.vs["cluster"] = clusters

# Adjust layout for clustering
# Get positions from the original layout
positions = g.layout("fr").coords

# Separate nodes based on clusters
for idx, cluster in enumerate(clusters):
    if cluster == "High Hub Score":
        positions[idx][1] -= 100  # Shift upwards
    else:
        positions[idx][1] += 100  # Shift downwards

layout = g.layout("fr, seed=positions")
"""
layout = g.layout("kk")


scaled_hub_scores = [min_size + (math.log(score + 1) * (max_size - min_size) / math.log(1 + max_hub_score)) for score in normalized_hub_score]

visual_style = {
    "vertex_size": scaled_hub_scores,
    "vertex_label": [f"{v['name']}\nAuth: {v['authority_score']:.4f}\nHub: {v['hub_score']:.4f}\nBetw: {v['betweenness']:.4f}" for v in g.vs],
    "vertex_color": ["red" if score > max(hub_score)/2 else "blue" for score in hub_score],
    "edge_color": "#D3D3D3",
    "background": "white",
    "bbox": (600, 600),
    "margin": 100
}

ig.plot(g, layout=layout, target="network_graph.png", **visual_style)