import networkx as nx
import matplotlib.pyplot as plt
import time

# Define the building as a graph
G = nx.DiGraph()

# Hardcoded nodes with additional rooms
nodes = ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14", "R15", "R16"]
exit_nodes = {"R2", "R9", "R16"}  # Fixed exit nodes
initial_fire_nodes = {"R4"}  # Fire starts here

# Add nodes to graph
for node in nodes:
    G.add_node(node, exit=node in exit_nodes, fire=False)

# Hardcoded edges (doors) with weights
edges = [
    ("R0", "R1"), ("R1", "R2"), ("R3", "R4"), ("R4", "R5"),
    ("R5", "R6"), ("R6", "R7"), ("R7", "R3"),  # Circular trap around R3
    ("R7", "R8"), ("R8", "R9"), ("R9", "R10"), ("R10", "R11"), ("R11", "R0"),
    ("R0", "R5"), ("R5", "R10"), ("R1", "R6"), ("R6", "R11"),
    ("R2", "R7"), ("R7", "R0"), ("R8", "R1"),
    ("R4", "R9"), ("R9", "R2"), ("R10", "R12"), ("R12", "R13"), ("R13", "R14"),
    ("R14", "R15"), ("R15", "R16"), ("R8", "R12"), ("R3", "R14")
]

for edge in edges:
    G.add_edge(edge[0], edge[1], weight=1)

# Function to find the safest and shortest path avoiding fire
def find_safest_paths(G, exit_nodes, fire_nodes):
    safe_paths = {}
    blocked_nodes = set()

    for node in G.nodes:
        if node in exit_nodes:
            safe_paths[node] = None
            continue
        shortest_path = None
        shortest_length = float("inf")
        for exit_node in exit_nodes:
            try:
                path = nx.shortest_path(G, source=node, target=exit_node, weight="weight")
                if any(n in fire_nodes for n in path):
                    continue
                length = nx.shortest_path_length(G, source=node, target=exit_node, weight="weight")
                if length < shortest_length:
                    shortest_path = path
                    shortest_length = length
            except nx.NetworkXNoPath:
                continue

        if shortest_path is None:
            blocked_nodes.add(node)
        safe_paths[node] = shortest_path

    return safe_paths, blocked_nodes

# Function to spread fire over time
def spread_fire(G, fire_nodes, steps=10, delay=3):
    burning_rooms = set(fire_nodes)
    plt.ion()
    for step in range(steps):
        new_fires = set()
        for node in burning_rooms:
            for neighbor in G.neighbors(node):
                if neighbor not in burning_rooms:
                    new_fires.add(neighbor)
        burning_rooms.update(new_fires)
        visualize_fire(G, burning_rooms, step)
        time.sleep(delay)
        if not plt.fignum_exists(1):
            return
    plt.ioff()
    plt.show()

# Function to visualize the fire at each step and show safest paths
def visualize_fire(G, fire_nodes, step):
    plt.clf()
    pos = nx.circular_layout(G)
    
    safe_paths, blocked_nodes = find_safest_paths(G, exit_nodes, fire_nodes)
    
    node_colors = [
        "red" if n in fire_nodes else 
        "blue" if G.nodes[n]["exit"] else 
        "orange" if n in blocked_nodes else 
        "green"
        for n in G.nodes
    ]
    
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=1000, edge_color="gray")
    
    for node, path in safe_paths.items():
        if path and len(path) > 1:
            for i in range(len(path) - 1):
                nx.draw_networkx_edges(G, pos, edgelist=[(path[i], path[i+1])], edge_color="blue", width=2, arrowstyle="->")
    
    plt.text(0.85, 0.9, f"Time: {step * 3}s", transform=plt.gca().transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.5))
    plt.title(f"Fire Spread - Step {step+1}")
    plt.pause(1)

spread_fire(G, initial_fire_nodes)
