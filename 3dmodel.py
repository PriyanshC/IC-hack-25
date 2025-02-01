import networkx as nx
import matplotlib.pyplot as plt
import random
from mpl_toolkits.mplot3d import Axes3D

# Define the 3D building structure
FLOORS = 3  # Number of floors
ROOMS_PER_FLOOR = 4  # Rooms per floor
TOTAL_NODES = FLOORS * ROOMS_PER_FLOOR  # Total rooms
STAIRWELLS = 2  # Number of stairwells

# Create a graph
G = nx.DiGraph()

# Generate nodes for rooms
nodes = [f"R{floor}_{room}" for floor in range(FLOORS) for room in range(ROOMS_PER_FLOOR)]
exit_nodes = {f"R0_{random.randint(0, ROOMS_PER_FLOOR - 1)}"}  # Exit on ground floor
fire_nodes = set(random.sample(nodes, 3))  # Random fire locations
stairwells = set(random.sample(nodes, STAIRWELLS))  # Random stairwells

# Add nodes to the graph
for node in nodes:
    G.add_node(node, exit=node in exit_nodes, fire=node in fire_nodes, stairwell=node in stairwells)

# Generate edges for rooms on the same floor
for floor in range(FLOORS):
    for i in range(ROOMS_PER_FLOOR):
        current = f"R{floor}_{i}"
        next_room = f"R{floor}_{(i + 1) % ROOMS_PER_FLOOR}"
        G.add_edge(current, next_room, weight=1)

# Connect stairwells between floors
for stairwell in stairwells:
    floor, room = map(int, stairwell[1:].split("_"))
    if floor < FLOORS - 1:  # Connect upwards
        G.add_edge(stairwell, f"R{floor + 1}_{room}", weight=1)
    if floor > 0:  # Connect downwards
        G.add_edge(stairwell, f"R{floor - 1}_{room}", weight=1)

# Function to find safest paths
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

# Compute safest paths
safe_paths, blocked_nodes = find_safest_paths(G, exit_nodes)

# 3D Visualization
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection="3d")

# Assign 3D positions
pos = {}
for node in G.nodes:
    floor, room = map(int, node[1:].split("_"))
    pos[node] = (room, floor, 0)  # (X, Y, Z)

# Node colors
node_colors = [
    "red" if G.nodes[n]["fire"] else 
    "blue" if G.nodes[n]["exit"] else 
    "orange" if n in blocked_nodes else 
    "yellow" if G.nodes[n]["stairwell"] else 
    "green"
    for n in G.nodes
]

# Draw nodes
for node, (x, y, z) in pos.items():
    ax.scatter(x, y, z, color=node_colors[list(G.nodes).index(node)], s=200)

# Draw edges
for edge in G.edges:
    x_vals, y_vals, z_vals = zip(*[pos[edge[0]], pos[edge[1]]])
    ax.plot(x_vals, y_vals, z_vals, "gray")

# Draw safest paths
for node, path in safe_paths.items():
    if path and len(path) > 1:
        for i in range(len(path) - 1):
            x_vals, y_vals, z_vals = zip(*[pos[path[i]], pos[path[i+1]]])
            ax.plot(x_vals, y_vals, z_vals, "blue", linewidth=2)

ax.set_xlabel("Room")
ax.set_ylabel("Floor")
ax.set_zlabel("Height")
ax.set_title("3D Building Escape Route")
plt.show()
