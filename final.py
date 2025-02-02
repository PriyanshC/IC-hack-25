import networkx as nx
import matplotlib.pyplot as plt
import random
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Building configuration
FLOORS = 5

# Create graph
G = nx.Graph()  # Use an undirected graph for bidirectional edges

nodes = [
    "R0_0_0",
    "R0_0_1",
    "R0_1_0"
]

[nodes.extend([
    f"R{floor}_0_0",
    f"R{floor}_0_1",
    f"R{floor}_0_2",
    f"R{floor}_0_3",
    f"R{floor}_0_4",

    F"R{floor}_1_2",

    f"R{floor}_2_0",
    f"R{floor}_2_1",
    f"R{floor}_2_2",
    f"R{floor}_2_3",
    f"R{floor}_2_4",
]) for floor in range(1, FLOORS)]

initial_fire_nodes = set(random.sample(nodes, 1))  # Start with 1 fire node
fire_nodes = set(initial_fire_nodes)
exit_nodes = ["R0_0_0", "R0_0_1"]

stairwell_nodes = ["R0_1_0", "R_0_1"]
[stairwell_nodes.extend([f"R{floor}_0_3", f"R{floor}_2_3"]) for floor in range(1, FLOORS - 1)]

# Add nodes to graph
for node in nodes:
    G.add_node(node, exit=node in exit_nodes, fire=node in fire_nodes, stairwell=node in stairwell_nodes, warning=float('inf'), distance_to_safety=float('inf'))


G.add_edge(f"R0_0_0", f"R0_0_1", weight=4)
G.add_edge(f"R0_0_0", f"R0_1_0", weight=4)
G.add_edge(f"R0_1_0", f"R1_0_0", weight=4)
G.add_edge(f"R0_0_1", f"R1_0_4", weight=4)


# Connect rooms within the same floor (bidirectional)
for floor in range(1, FLOORS):
    G.add_edge(f"R{floor}_0_0", f"R{floor}_0_1", weight=4)
    G.add_edge(f"R{floor}_0_1", f"R{floor}_0_2", weight=4)
    G.add_edge(f"R{floor}_0_2", f"R{floor}_0_3", weight=4)
    G.add_edge(f"R{floor}_0_3", f"R{floor}_0_4", weight=4)
    
    G.add_edge(f"R{floor}_0_2", f"R{floor}_1_2", weight=4)
    G.add_edge(f"R{floor}_1_2", f"R{floor}_2_2", weight=4)
    
    G.add_edge(f"R{floor}_2_0", f"R{floor}_2_1", weight=4)
    G.add_edge(f"R{floor}_2_1", f"R{floor}_2_2", weight=4)
    G.add_edge(f"R{floor}_2_2", f"R{floor}_2_3", weight=4)
    G.add_edge(f"R{floor}_2_3", f"R{floor}_2_4", weight=4)


# Connect floors via stairwell (bidirectional)
for floor in range(1, FLOORS - 1):
    G.add_edge(f"R{floor}_0_3", f"R{floor + 1}_0_3", weight=4)
    G.add_edge(f"R{floor}_2_3", f"R{floor + 1}_2_3", weight=4)

    
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
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection="3d")

fire_spread_time = 1
time_since_fire = 0
tick_speed = 500  # Milliseconds per tick

def update(frame):
    global fire_spread_time, time_since_fire, tick_speed, paused
    
    if paused:
        return  # Skip updating when paused
    
    ax.clear()
    time_since_fire += 1
    if fire_spread_time >= 2 * (1000 / tick_speed):  # Fire spreads every 2 seconds
        spread_fire()
        calculate_fire_eta(G, fire_nodes, tick_speed)  # Update fire ETA for all nodes
        calculate_distance_to_safety(G, exit_nodes)  # Update distance to safety for all nodes
        fire_spread_time = 0    
    fire_spread_time += 1 

    safe_paths, blocked_nodes = find_safest_paths(G, exit_nodes)
    
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
        ax.scatter(x, y, z, color=color, s=200)

        # Get node attributes
        # distance_to_safety = G.nodes[node]["distance_to_safety"]
        # fire_eta = G.nodes[node]["warning"]
        
        # # Display distance to safety above the node
        # ax.text(x, y, z + 0.3, f"{distance_to_safety:.1f}", color="blue", fontsize=10, ha="center")

        # # Display warning time (fire ETA) below the node
        # ax.text(x, y, z - 0.3, f"{fire_eta:.1f}", color="red", fontsize=10, ha="center")

    for edge in G.edges:
        x_vals, y_vals, z_vals = zip(*[pos[edge[0]], pos[edge[1]]])
        ax.plot(x_vals, y_vals, z_vals, "gray")
    
    for node, path in safe_paths.items():
        if path and len(path) > 1:
            for i in range(len(path) - 1):
                x_vals, y_vals, z_vals = zip(*[pos[path[i]], pos[path[i+1]]])
                ax.plot(x_vals, y_vals, z_vals, "blue", linewidth=2)

    # Draw the person smoothly moving
    ax.scatter(*person.current_position, color="pink", s=250, edgecolor="white")

    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    ax.set_zlabel("Floor")
    ax.set_title(f"Time Step: {frame+1}")

    
paused = False  # Global pause state

def on_key_press(event):
    global paused
    if event.key == " ":
        paused = not paused  # Toggle pause/play

ani = FuncAnimation(fig, update, interval=tick_speed)
fig.canvas.mpl_connect("key_press_event", on_key_press)

plt.show()