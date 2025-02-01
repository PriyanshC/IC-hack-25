import networkx as nx
import matplotlib.pyplot as plt
import random

# Define the building as a graph
G = nx.DiGraph()

# Nodes (Rooms & Corridors)
nodes = [f"R{i}" for i in range(12)]
exit_nodes = random.sample(nodes, 2)  # Randomly select 2 exit nodes
fire_nodes = random.sample(set(nodes) - set(exit_nodes), 3)  # 3 random fire nodes

# Add nodes to graph
for node in nodes:
    G.add_node(node, exit=(node in exit_nodes), fire=(node in fire_nodes))

# Define edges (Doors) with weights (distance/time to travel)
edges = [
    ("R0", "R1"), ("R1", "R2"), ("R2", "R3"), ("R3", "R4"), ("R4", "R5"),
    ("R5", "R6"), ("R6", "R7"), ("R7", "R8"), ("R8", "R9"), ("R9", "R10"),
    ("R10", "R11"), ("R11", "R0"), ("R0", "R5"), ("R5", "R10"),
    ("R1", "R6"), ("R6", "R11"), ("R2", "R7"), ("R7", "R0"), ("R3", "R8"),
    ("R8", "R1"), ("R4", "R9"), ("R9", "R2")
]
for edge in edges:
    G.add_edge(edge[0], edge[1], weight=random.randint(1, 5))

# Function to find the safest and shortest path avoiding fire
def find_safest_paths(G, exit_nodes):
    safe_paths = {}
    for node in G.nodes:
        if node in exit_nodes:
            safe_paths[node] = None  # No path needed for exit nodes
            continue
        shortest_path = None
        shortest_length = float("inf")
        for exit_node in exit_nodes:
            try:
                path = nx.shortest_path(G, source=node, target=exit_node, weight="weight")
                if any(n in fire_nodes for n in path):  # Avoid paths through fire
                    continue
                length = nx.shortest_path_length(G, source=node, target=exit_node, weight="weight")
                if length < shortest_length:
                    shortest_path = path
                    shortest_length = length
            except nx.NetworkXNoPath:
                continue
        safe_paths[node] = shortest_path
    return safe_paths

# Get the safest paths
safe_paths = find_safest_paths(G, exit_nodes)

# Draw the graph
plt.figure(figsize=(10, 7))
pos = nx.spring_layout(G)  # Positioning nodes

# Color nodes based on fire/safety
node_colors = ["red" if G.nodes[n]["fire"] else "green" for n in G.nodes]
nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=1000, edge_color="gray")

# Draw safest paths with arrows
for node, path in safe_paths.items():
    if path and len(path) > 1:
        for i in range(len(path) - 1):
            nx.draw_networkx_edges(G, pos, edgelist=[(path[i], path[i+1])], edge_color="blue", width=2, arrowstyle="->")

plt.title("Building Escape Route")
plt.show()
