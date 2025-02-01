import networkx as nx
import matplotlib.pyplot as plt
import random
from mpl_toolkits.mplot3d import Axes3D

# Building configuration
FLOORS = 3
ROWS = 3  # Rows of rooms per floor
COLS = 4  # Columns of rooms per floor

# Create graph
G = nx.DiGraph()

# Generate nodes for a structured layout
nodes = []
for floor in range(FLOORS):
    for row in range(ROWS):
        for col in range(COLS):
            nodes.append(f"R{floor}_{row}_{col}")

# Choose a fixed central stairwell position
stairwell_row, stairwell_col = ROWS // 2, COLS // 2
stairwell_nodes = {f"R{floor}_{stairwell_row}_{stairwell_col}" for floor in range(FLOORS)}

# Randomly choose exits and fire locations
exit_nodes = {f"R0_{random.randint(0, ROWS-1)}_{random.randint(0, COLS-1)}"}  # Exit on ground floor
fire_nodes = set(random.sample(nodes, 4))  # Random fire locations

# Add nodes to graph
for node in nodes:
    G.add_node(node, exit=node in exit_nodes, fire=node in fire_nodes, stairwell=node in stairwell_nodes)

# Connect rooms within the same floor
for floor in range(FLOORS):
    for row in range(ROWS):
        for col in range(COLS):
            current = f"R{floor}_{row}_{col}"
            # Right neighbor
            if col < COLS - 1:
                G.add_edge(current, f"R{floor}_{row}_{col + 1}", weight=1)
            # Left neighbor
            if col > 0:
                G.add_edge(current, f"R{floor}_{row}_{col - 1}", weight=1)
            # Down neighbor
            if row < ROWS - 1:
                G.add_edge(current, f"R{floor}_{row + 1}_{col}", weight=1)
            # Up neighbor
            if row > 0:
                G.add_edge(current, f"R{floor}_{row - 1}_{col}", weight=1)

# Connect floors using only the single stairwell
for floor in range(FLOORS - 1):  # Connect floor i to i+1
    lower = f"R{floor}_{stairwell_row}_{stairwell_col}"
    upper = f"R{floor + 1}_{stairwell_row}_{stairwell_col}"
    G.add_edge(lower, upper, weight=1)
    G.add_edge(upper, lower, weight=1)

# Function to find safest paths
def find_safest_paths(G, exit_nodes):
    safe_paths = {}
    blocked_nodes = set()  # Nodes with no escape

    for node in G.nodes:
        if node in exit_nodes:
            safe_paths[node] = None  # No path needed for exit nodes
            continue
        shortest_path = None
        shortest_length = float("inf")
        for exit_node in exit_nodes:
            try:
                path = nx.shortest_path(G, source=node, target=exit_node, weight="weight")
                if all(n not in fire_nodes for n in path):  # Ensure path is fully safe
                    length = nx.shortest_path_length(G, source=node, target=exit_node, weight="weight")
                    if length < shortest_length:
                        shortest_path = path
                        shortest_length = length
            except nx.NetworkXNoPath:
                continue

        if shortest_path is None:
            blocked_nodes.add(node)  # Mark as isolated only if no valid path exists
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
    floor, row, col = map(int, node[1:].split("_"))
    pos[node] = (col, row, floor)  # (X, Y, Z)

# Node colors
node_colors = [
    "red" if G.nodes[n]["fire"] else 
    "blue" if G.nodes[n]["exit"] else 
    "orange" if n in blocked_nodes else 
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

ax.set_xlabel("Column")
ax.set_ylabel("Row")
ax.set_zlabel("Floor")
ax.set_title("3D Structured Building Escape Route")
plt.show()
