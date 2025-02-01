import networkx as nx
import matplotlib.pyplot as plt
import random
import time
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Building configuration
FLOORS = 3
ROWS = 3
COLS = 4

# Create graph
G = nx.DiGraph()

# Generate nodes
nodes = [f"R{floor}_{row}_{col}" for floor in range(FLOORS) for row in range(ROWS) for col in range(COLS)]
stairwell_row, stairwell_col = ROWS // 2, COLS // 2
stairwell_nodes = {f"R{floor}_{stairwell_row}_{stairwell_col}" for floor in range(FLOORS)}
exit_nodes = {f"R0_{random.randint(0, ROWS-1)}_{random.randint(0, COLS-1)}"}  # Random exit
initial_fire_nodes = set(random.sample(nodes, 1))  # Start with 1 fire nodes
fire_nodes = set(initial_fire_nodes)

# Add nodes to graph
for node in nodes:
    G.add_node(node, exit=node in exit_nodes, fire=node in fire_nodes, stairwell=node in stairwell_nodes)

# Connect rooms within the same floor
for floor in range(FLOORS):
    for row in range(ROWS):
        for col in range(COLS):
            current = f"R{floor}_{row}_{col}"
            if col < COLS - 1: G.add_edge(current, f"R{floor}_{row}_{col + 1}", weight=1)
            if col > 0: G.add_edge(current, f"R{floor}_{row}_{col - 1}", weight=1)
            if row < ROWS - 1: G.add_edge(current, f"R{floor}_{row + 1}_{col}", weight=1)
            if row > 0: G.add_edge(current, f"R{floor}_{row - 1}_{col}", weight=1)

# Connect floors via stairwell
for floor in range(FLOORS - 1):
    lower, upper = f"R{floor}_{stairwell_row}_{stairwell_col}", f"R{floor + 1}_{stairwell_row}_{stairwell_col}"
    G.add_edge(lower, upper, weight=1)
    G.add_edge(upper, lower, weight=1)

# Function to find safest paths
def find_safest_paths(G, exit_nodes):
    safe_paths = {}
    blocked_nodes = set()
    for node in G.nodes:
        if node in exit_nodes:
            safe_paths[node] = None
            continue
        valid_paths = []
        for exit_node in exit_nodes:
            try:
                paths = list(nx.all_simple_paths(G, source=node, target=exit_node))
                for path in paths:
                    if all(n not in fire_nodes for n in path):
                        valid_paths.append(path)
            except nx.NetworkXNoPath:
                continue
        safe_paths[node] = min(valid_paths, key=len) if valid_paths else None
        if not safe_paths[node]:
            blocked_nodes.add(node)
    return safe_paths, blocked_nodes

# Fire spread function
def spread_fire():
    new_fire_nodes = set()
    for node in fire_nodes:
        floor, row, col = map(int, node[1:].split("_"))
        neighbors = [
            f"R{floor}_{row+1}_{col}", f"R{floor}_{row-1}_{col}",
            f"R{floor}_{row}_{col+1}", f"R{floor}_{row}_{col-1}"
        ]
        if node in stairwell_nodes and floor < FLOORS - 1:
            neighbors.append(f"R{floor+1}_{row}_{col}")
        if node in stairwell_nodes and floor > 0:
            neighbors.append(f"R{floor-1}_{row}_{col}")
        
        # Filter neighbors that are not on fire yet
        uninfected_neighbors = [n for n in neighbors if n not in fire_nodes and n in G.nodes]
        
        # If there are any uninfected neighbors, randomly pick one to infect
        if uninfected_neighbors:
            new_fire_node = random.choice(uninfected_neighbors)
            if new_fire_node not in exit_nodes:
                new_fire_nodes.add(new_fire_node)
    
    # Update fire nodes
    fire_nodes.update(new_fire_nodes)
    for node in fire_nodes:
        G.nodes[node]["fire"] = True


# 3D Visualization
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection="3d")

# Assign 3D positions
pos = {node: (int(node.split("_")[2]), int(node.split("_")[1]), int(node.split("_")[0][1:])) for node in G.nodes}

def update(frame):
    ax.clear()
    spread_fire()
    safe_paths, blocked_nodes = find_safest_paths(G, exit_nodes)
    
    node_colors = [
        "red" if G.nodes[n]["fire"] else
        "blue" if G.nodes[n]["exit"] else
        "orange" if n in blocked_nodes else
        "green" for n in G.nodes
    ]
    
    for node, (x, y, z) in pos.items():
        ax.scatter(x, y, z, color=node_colors[list(G.nodes).index(node)], s=200)
    
    for edge in G.edges:
        x_vals, y_vals, z_vals = zip(*[pos[edge[0]], pos[edge[1]]])
        ax.plot(x_vals, y_vals, z_vals, "gray")
    
    for node, path in safe_paths.items():
        if path and len(path) > 1:
            for i in range(len(path) - 1):
                x_vals, y_vals, z_vals = zip(*[pos[path[i]], pos[path[i+1]]])
                ax.plot(x_vals, y_vals, z_vals, "blue", linewidth=2)
    
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    ax.set_zlabel("Floor")
    ax.set_title(f"Time Step: {frame+1}")

ani = FuncAnimation(fig, update, frames=1, interval=3000)
plt.show()
