import json
import igraph as ig

# Read JSON file containing packet data
with open(".json", "r") as f:
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
# for example, port number, timestamp, etc.
for packet in packets:
    edge_id = g.get_eid(packet["src_ip"], packet["dst_ip"])
    g.es[edge_id]["src_port"] = packet["src_port"]
    g.es[edge_id]["dst_port"] = packet["dst_port"]
    g.es[edge_id]["timestamp"] = packet["timestamp"]

# Visualize the graph
layout = g.layout("kk")  # Kamada-Kaway layout
ig.plot(g, layout=layout, target="network_graph.png")

