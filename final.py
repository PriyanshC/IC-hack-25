import networkx as nx
import matplotlib.pyplot as plt
import random
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np

# Load images for visual indicators (replace with your own images if needed)
fire_exit_sign = plt.imread("fire_exit.png")  # Replace with path to fire exit sign image
red_cross = plt.imread("red_cross.png")      # Replace with path to red cross image
triangle = plt.imread("trapped.png")        # Replace with path to triangle image
running_man = plt.imread("rush.png")  # Replace with path to running man image
not_fastest_route = plt.imread("faster_route.png")  # Replace with path to the image


# Building configuration
FLOORS = 3
ROWS = 3
COLS = 4

# Create graph
G = nx.Graph()  # Use an undirected graph for bidirectional edges

# Generate nodes
nodes = [f"R{floor}_{row}_{col}" for floor in range(FLOORS) for row in range(ROWS) for col in range(COLS)]
stairwell_row, stairwell_col = ROWS // 2, COLS // 2
stairwell_nodes = {f"R{floor}_{stairwell_row}_{stairwell_col}" for floor in range(FLOORS)}
exit_nodes = {f"R0_0_0"}  # Random exit
initial_fire_nodes = {"R2_2_0"}  # Start with 1 fire node
fire_nodes = set(initial_fire_nodes)

# Add nodes to graph
for node in nodes:
    G.add_node(node, exit=node in exit_nodes, fire=node in fire_nodes, stairwell=node in stairwell_nodes, warning=float('inf'), distance_to_safety=float('inf'))

# Connect rooms within the same floor (bidirectional)
for floor in range(FLOORS):
    for row in range(ROWS):
        for col in range(COLS):
            current = f"R{floor}_{row}_{col}"
            if col < COLS - 1: G.add_edge(current, f"R{floor}_{row}_{col + 1}", weight=4)
            if col > 0: G.add_edge(current, f"R{floor}_{row}_{col - 1}", weight=4)
            if row < ROWS - 1: G.add_edge(current, f"R{floor}_{row + 1}_{col}", weight=4)
            if row > 0: G.add_edge(current, f"R{floor}_{row - 1}_{col}", weight=4)

# Connect floors via stairwell (bidirectional)
for floor in range(FLOORS - 1):
    lower, upper = f"R{floor}_{stairwell_row}_{stairwell_col}", f"R{floor + 1}_{stairwell_row}_{stairwell_col}"
    G.add_edge(lower, upper, weight=4)

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
        safe_paths[node] = min(valid_paths, key=lambda p: sum(G.edges[edge]['weight'] for edge in zip(p[:-1], p[1:]))) if valid_paths else None
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

# Function to calculate fire ETA for each node based on the safest path
def calculate_fire_eta(G, fire_nodes, tick_speed):
    # Initialize all warnings to infinity
    for node in G.nodes:
        G.nodes[node]["warning"] = float('inf')
    
    # For each fire node, calculate the shortest path to all other nodes
    for fire_node in fire_nodes:
        lengths = nx.single_source_dijkstra_path_length(G, fire_node, weight='weight')
        for node, length in lengths.items():
            # Scale the warning time by tick speed and add randomness
            fire_spread_rate = 1  # Random fire spread rate
            # fire_spread_rate = random.uniform(0.5, 1.5)  # Random fire spread rate
            
            warning_time = (length * (1000 / tick_speed)) / fire_spread_rate
            if warning_time < G.nodes[node]["warning"]:
                G.nodes[node]["warning"] = warning_time

    # Update warning values to reflect the minimum fire spread value along the safest path
    safe_paths, _ = find_safest_paths(G, exit_nodes)
    for node, path in safe_paths.items():
        if path:
            # Find the minimum fire spread value along the safest path
            min_fire_warning = min(G.nodes[n]["warning"] for n in path)
            G.nodes[node]["warning"] = min_fire_warning

# Function to calculate distance to safety (exit) for each node
def calculate_distance_to_safety(G, exit_nodes):
    for node in G.nodes:
        G.nodes[node]["distance_to_safety"] = float('inf')
    for exit_node in exit_nodes:
        lengths = nx.single_source_dijkstra_path_length(G, exit_node, weight='weight')
        for node, length in lengths.items():
            if length < G.nodes[node]["distance_to_safety"]:
                G.nodes[node]["distance_to_safety"] = length

class Person:
    def __init__(self, start_node, pos):
        self.pos = pos
        self.current_node = start_node
        self.target_node = None
        self.t = 0  # Interpolation factor (0 → start node, 1 → target node)
        self.current_position = self.pos[start_node]  # Start at node position
        self.speed = 0.1  # Default speed

    def move(self, safe_paths):
        global tick_speed
        if self.target_node is None or self.t == 0:
            path = safe_paths[self.current_node]
            if path and len(path) > 1:
                self.current_node = path[0]
                self.target_node = path[1]
                self.t = 0  # Reset interpolation factor
                # Update speed based on edge weight and tick speed
                edge_weight = G.edges[self.current_node, self.target_node]['weight']
                self.speed = 1 / (edge_weight * (1000 / tick_speed))  # Speed is inversely proportional to weight
            else:
                self.target_node = None  # No movement if no path found

    def update_position(self):
        if self.target_node:
            start_pos = self.pos[self.current_node]
            end_pos = self.pos[self.target_node]
            
            # Linear interpolation between start and end positions
            self.current_position = (
                (1 - self.t) * start_pos[0] + self.t * end_pos[0],  # X
                (1 - self.t) * start_pos[1] + self.t * end_pos[1],  # Y
                (1 - self.t) * start_pos[2] + self.t * end_pos[2]   # Z
            )
            
            self.t += self.speed  # Move smoothly based on speed
            if self.t >= 1:  # If reached target, snap to node
                self.current_node = self.target_node
                self.t = 0  # Reset for next movement

# Assign 3D positions
pos = {node: (int(node.split("_")[2]), int(node.split("_")[1]), int(node.split("_")[0][1:])) for node in G.nodes}

# Initialize person
person = Person("R2_0_0", pos)

# 3D Visualization
# fig = plt.figure(figsize=(10, 7))
# ax = fig.add_subplot(111, projection="3d")

fire_spread_time = 1
time_since_fire = 0
tick_speed = 500  # Milliseconds per tick



def update_edge_states(G, safe_paths, blocked_nodes):
    # Reset all edge states to "not fastest route"
    for u, v in G.edges:
        G.edges[u, v]["state"] = "not fastest route"
        G.edges[v, u]["state"] = "not fastest route"


    # Handle "trapped" state for blocked nodes
    for node in blocked_nodes:
        for neighbor in G.neighbors(node):
            G.edges[node, neighbor]["state"] = "trapped"
            G.edges[neighbor, node]["state"] = "trapped"

    # Mark edges leading into fire as "fire ahead"
    for node in G.nodes:
        if G.nodes[node]["fire"]:
            for neighbor in G.neighbors(node):
                G.edges[neighbor, node]["state"] = "fire ahead"  # Edge leading into fire

    # Mark edges along the safest path as "safe route"
    for node, path in safe_paths.items():
        if path and len(path) > 1:
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                if G.edges[u, v]["state"] != "fire ahead":  # Only mark as safe if not leading into fire
                    G.edges[u, v]["state"] = "safe route"

    # Handle "go faster" state for yellow nodes
    for node in G.nodes:
        if G.nodes[node]["warning"] < G.nodes[node]["distance_to_safety"]:
            path = safe_paths[node]
            if path and len(path) > 1:
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    if G.nodes[v]["warning"] < G.nodes[v]["distance_to_safety"]:
                        G.edges[u, v]["state"] = "go faster"


            
            
def create_mini_ui(ax, edge_states):
    ax.clear()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")

    # Create a grid layout for the mini UI
    n_edges = len(edge_states)
    n_cols = int(np.ceil(np.sqrt(n_edges)))
    n_rows = int(np.ceil(n_edges / n_cols))

    # Define state-to-digit mapping
    state_to_digit = {
        "safe route": 0,
        "not fastest route": 1,
        "go faster": 2,
        "trapped": 3,
        "fire ahead": 4,
    }

    # Define state-to-color mapping
    state_to_color = {
        "safe route": "green",
        "not fastest route": "orange",
        "go faster": "yellow",
        "trapped": "black",
        "fire ahead": "red",
    }

    for idx, (edge, state) in enumerate(edge_states.items()):
        row = idx // n_cols
        col = idx % n_cols
        x = col * (10 / n_cols) + (5 / n_cols)
        y = 10 - (row * (10 / n_rows) + (5 / n_rows))

        # Get the digit and color for the current state
        digit = state_to_digit.get(state, 0)  # Default to 0 if state is not found
        color = state_to_color.get(state, "green")  # Default to green if state is not found

        # Display the digit in the grid cell
        ax.text(
            x, y, str(digit), color=color, fontsize=20, ha="center", va="center", fontweight="bold"
        )
# Modify the update function to include the mini UI
def update(frame):
    global fire_spread_time, time_since_fire, tick_speed, paused

    if paused:
        return  # Skip updating when paused

    ax_3d.clear()
    time_since_fire += 1
    if fire_spread_time >= 2 * (1000 / tick_speed):  # Fire spreads every 2 seconds
        spread_fire()
        calculate_fire_eta(G, fire_nodes, tick_speed)  # Update fire ETA for all nodes
        calculate_distance_to_safety(G, exit_nodes)  # Update distance to safety for all nodes
        fire_spread_time = 0
    fire_spread_time += 1

    safe_paths, blocked_nodes = find_safest_paths(G, exit_nodes)
    update_edge_states(G, safe_paths, blocked_nodes)  # Update edge states for both directions

    # Move the person gradually
    person.update_position()
    person.move(safe_paths)

    # Node colors based on fire, exit, warning, and blocked status
    node_colors = [
        "red" if G.nodes[n]["fire"] else
        "blue" if G.nodes[n]["exit"] else
        "orange" if n in blocked_nodes else
        "yellow" if G.nodes[n]["warning"] < G.nodes[n]["distance_to_safety"] else
        "green" for n in G.nodes
    ]

    for node, (x, y, z) in pos.items():
        color = node_colors[list(G.nodes).index(node)]
        ax_3d.scatter(x, y, z, color=color, s=200)

    # Draw edges with their states for both directions
    for u, v in G.edges:
        x_vals, y_vals, z_vals = zip(*[pos[u], pos[v]])
        edge_state_forward = G.edges[u, v]["state"]
        edge_state_backward = G.edges[v, u]["state"]

        # Draw forward direction (u → v)
        if edge_state_forward == "safe route":
            ax_3d.plot(x_vals, y_vals, z_vals, "blue", linewidth=2)
        elif edge_state_forward == "fire ahead":
            ax_3d.plot(x_vals, y_vals, z_vals, "red", linewidth=1, linestyle="dashed")
        elif edge_state_forward == "go faster":
            ax_3d.plot(x_vals, y_vals, z_vals, "yellow", linewidth=3)
        elif edge_state_forward == "trapped":
            ax_3d.plot(x_vals, y_vals, z_vals, "black", linewidth=1, linestyle="dotted")
        elif edge_state_forward == "not fastest route":
            ax_3d.plot(x_vals, y_vals, z_vals, "orange", linewidth=1, linestyle="dotted")

        # Draw backward direction (v → u)
        if edge_state_backward == "safe route":
            ax_3d.plot(x_vals, y_vals, z_vals, "blue", linewidth=2)
        elif edge_state_backward == "fire ahead":
            ax_3d.plot(x_vals, y_vals, z_vals, "red", linewidth=1, linestyle="dashed")
        elif edge_state_backward == "go faster":
            ax_3d.plot(x_vals, y_vals, z_vals, "yellow", linewidth=3)
        elif edge_state_backward == "trapped":
            ax_3d.plot(x_vals, y_vals, z_vals, "black", linewidth=1, linestyle="dotted")
        elif edge_state_backward == "not fastest route":
            ax_3d.plot(x_vals, y_vals, z_vals, "orange", linewidth=1, linestyle="dotted")

    # Draw the person smoothly moving
    ax_3d.scatter(*person.current_position, color="pink", s=250, edgecolor="white")

    ax_3d.set_xlabel("Column")
    ax_3d.set_ylabel("Row")
    ax_3d.set_zlabel("Floor")
    ax_3d.set_title(f"Time Step: {frame+1}")

    # Update the mini UI
    edge_states = {(u, v): G.edges[u, v]["state"] for u, v in G.edges}
    create_mini_ui(ax_ui, edge_states)
    
    
    
# Create the figure and subplots
fig = plt.figure(figsize=(15, 7))
gs = fig.add_gridspec(1, 2, width_ratios=[2, 1])
ax_3d = fig.add_subplot(gs[0], projection="3d")
ax_ui = fig.add_subplot(gs[1])

# Rest of the code remains the same


    
paused = False  # Global pause state

def on_key_press(event):
    global paused
    if event.key == " ":
        paused = not paused  # Toggle pause/play

ani = FuncAnimation(fig, update, interval=tick_speed)
fig.canvas.mpl_connect("key_press_event", on_key_press)

plt.show()