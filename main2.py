import networkx as nx
import matplotlib.pyplot as plt

# Define the building as a graph
G = nx.DiGraph()

# Hardcoded nodes
nodes = ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11"]
exit_nodes = {"R2", "R9"}  # Fixed exit nodes
fire_nodes = {"R4", "R5", "R6", "R7"}  # Fire surrounding R3

# Add nodes to graph
for node in nodes:
    G.add_node(node, exit=node in exit_nodes, fire=node in fire_nodes)

# Hardcoded edges (doors) with weights
edges = [
    ("R0", "R1"), ("R1", "R2"), ("R3", "R4"), ("R4", "R5"),
    ("R5", "R6"), ("R6", "R7"), ("R7", "R3"),  # Circular trap around R3
    ("R7", "R8"), ("R8", "R9"), ("R9", "R10"), ("R10", "R11"), ("R11", "R0"),
    ("R0", "R5"), ("R5", "R10"), ("R1", "R6"), ("R6", "R11"),
    ("R2", "R7"), ("R7", "R0"), ("R8", "R1"),
    ("R4", "R9"), ("R9", "R2")
]

for edge in edges:
    G.add_edge(edge[0], edge[1], weight=1)  # Fixed weight for consistency

# Function to find the safest and shortest path avoiding fire
def find_safest_paths(G, exit_nodes):
    safe_paths = {}
    blocked_nodes = set()  # Nodes with no escape route

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

        if shortest_path is None:
            blocked_nodes.add(node)  # Mark as isolated
        safe_paths[node] = shortest_path

    return safe_paths, blocked_nodes

# Get the safest paths & identify blocked nodes
safe_paths, blocked_nodes = find_safest_paths(G, exit_nodes)

# Draw the graph
plt.figure(figsize=(10, 7))
pos = nx.spring_layout(G)  # Positioning nodes

# Assign colors based on node type
node_colors = [
    "red" if G.nodes[n]["fire"] else 
    "blue" if G.nodes[n]["exit"] else 
    "orange" if n in blocked_nodes else 
    "green"
    for n in G.nodes
]

# Draw nodes and edges
nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=1000, edge_color="gray")

# Draw safest paths with arrows
for node, path in safe_paths.items():
    if path and len(path) > 1:
        for i in range(len(path) - 1):
            nx.draw_networkx_edges(G, pos, edgelist=[(path[i], path[i+1])], edge_color="blue", width=2, arrowstyle="->")

plt.title("Building Escape Route with Blocked Nodes")
plt.show()
