import threading
import networkx as nx
import matplotlib.pyplot as plt
import random
import time
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from server import Server
from building import *




# Fire spread function
def spread_fire(server):
    new_fire_nodes = set()
    for node in server.fire_nodes:
        floor, row, col = node.floor, node.row, node.col
        neighbors = []
        if row != 0:
            neighbors.append(server.findIndex(floor, row-1, col))
        if row != server.ROWS - 1:
            neighbors.append(server.findIndex(floor, row+1, col))
        if col != 0:
            neighbors.append(server.findIndex(floor, row, col-1))
        if col != server.COLS - 1:
            neighbors.append(server.findIndex(floor, row, col+1))
        
        if node in server.stairwell_nodes and floor < server.FLOORS - 1:
            neighbors.append(server.findIndex(floor+1, row, col))
        if node in server.stairwell_nodes and floor > 0:
            neighbors.append(server.findIndex(floor-1, row, col))

        
        # Filter neighbors that are not on fire yet
        uninfected_neighbors = [n for n in neighbors if n not in server.fire_nodes]
        
        # If there are any uninfected neighbors, randomly pick one to infect
        if uninfected_neighbors:
            new_fire_node = random.choice(uninfected_neighbors)
            if new_fire_node not in server.exit_nodes:
                new_fire_nodes.add(new_fire_node)



    
    # Update fire nodes
    for node in new_fire_nodes:
        server.updateRoom(node.floor, node.row, node.col, RoomState.Fire)





# Function to calculate fire ETA for each node based on the safest path
def calculate_fire_eta(G, fire_nodes, tick_speed, server):
    # Initialize all warnings to infinity
    for node in G.nodes:
        G.nodes[node]["warning"] = float('inf')
    
    # For each fire node, calculate the shortest path to all other nodes
    for fire_node in fire_nodes:
        lengths = nx.single_source_dijkstra_path_length(G, fire_node.name, weight='weight')
        for node, length in lengths.items():
            # Scale the warning time by tick speed and add randomness
            fire_spread_rate = 1  # Random fire spread rate
            # fire_spread_rate = random.uniform(0.5, 1.5)  # Random fire spread rate
            
            warning_time = (length * (1000 / tick_speed)) / fire_spread_rate
            if warning_time < G.nodes[node]["warning"]:
                G.nodes[node]["warning"] = warning_time

    # Update warning values to reflect the minimum fire spread value along the safest path
    safe_paths, _ = server.calculateExitRoutes()
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
        lengths = nx.single_source_dijkstra_path_length(G, exit_node.name, weight='weight')
        for node, length in lengths.items():
            if length < G.nodes[node]["distance_to_safety"]:
                G.nodes[node]["distance_to_safety"] = length
                if G.nodes[node]["warning"] < G.nodes[node]["distance_to_safety"]:
                     server.updateRoom(int(node.split("_")[0][1:]), int(node.split("_")[1]), int(node.split("_")[2]), RoomState.Hurry)
                

class Person:
    def __init__(self, start_node, pos, tick_speed=500):
        self.tick_speed = tick_speed
        self.pos = pos
        self.current_node = start_node
        self.target_node = None
        self.t = 0  # Interpolation factor (0 → start node, 1 → target node)
        self.current_position = self.pos[start_node]  # Start at node position
        self.speed = 0.1  # Default speed


    def move(self, safe_paths):
        if self.target_node is None or self.t == 0:
            path = safe_paths[self.current_node]
            if path and len(path) > 1:
                self.current_node = path[0]
                self.target_node = path[1]
                self.t = 0  # Reset interpolation factor
                
                
                # get the node between the room and get the weight
                edge_weight = server.state.edges[self.current_node, self.target_node]['weight']
                self.speed = 1 / (edge_weight * (1000 / self.tick_speed))  # Speed is inversely proportional to weight

            else:
                self.target_node = None  # No movement if no path found

    def update_position(self, speed=0.1):
        if self.target_node:
            start_pos = self.pos[self.current_node]
            end_pos = self.pos[self.target_node]
            
            # Linear interpolation between start and end positions
            self.current_position = (
                (1 - self.t) * start_pos[0] + self.t * end_pos[0],  # X
                (1 - self.t) * start_pos[1] + self.t * end_pos[1],  # Y
                (1 - self.t) * start_pos[2] + self.t * end_pos[2]   # Z
            )
            
            self.t += speed  # Move smoothly
            if self.t >= 1:  # If reached target, snap to node
                self.current_node = self.target_node
                self.t = 0  # Reset for next movement


def updateGraph(frame, server, pos, tick_speed):
    
    global paused, time_since_fire, fire_spread_time
    
    if paused:
        return  # Skip updating when paused

    ax.clear()
    G = server.pollState()
    
    
    if server.fire_nodes:
        time_since_fire += 1
        
        if fire_spread_time >= 2 * (1000 / tick_speed):  # Fire spreads every 2 seconds
            spread_fire(server)
            calculate_fire_eta(G, server.fire_nodes, tick_speed, server)  # Update fire ETA for all nodes
            calculate_distance_to_safety(G, server.exit_nodes)  # Update distance to safety for all nodes
            fire_spread_time = 0    
        fire_spread_time += 1 
        
        safe_paths, blocked_nodes = server.calculateExitRoutes()

        person.update_position(speed=0.2)  # Adjust speed as needed
        person.move(safe_paths)
    else:
        safe_paths, blocked_nodes = server.calculateExitRoutes()

        
    
    
    # Move the person gradually
    
    
    
    # each node has a time, which tells us when the fire will reach
    # no fire means node warning = sys.time.max
    
    # G.nodes[n]["warning"] = 20 // eta time of arrival of fireat that node

    node_colors = [
        "red" if G.nodes[n]["fire"] else
        "blue" if G.nodes[n]["exit"] else
        "orange" if n in blocked_nodes else
        "yellow" if G.nodes[n]["warning"] < G.nodes[n]["distance_to_safety"] else
        "green" for n in G.nodes
    ]

    for i, (node, (x, y, z)) in enumerate(pos.items()):
        ax.scatter(x, y, z, color=node_colors[i], s=200)
    
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

def displayThread(server, pos):
    ani = FuncAnimation(fig, updateGraph, fargs=(server, pos, tick_speed), interval=tick_speed)
    plt.show()

def inputThread(server):
    while True:
        user_input = input("Enter command (fire ROOM / exit): ").strip()
        if user_input == "exit":
            break
        elif user_input.startswith("fire "):
            _, floor, row, col = user_input.split()
            floor, row, col = int(floor), int(row), int(col)
            if Room(floor, row, col) in server.getNodes():
                server.updateRoom(floor, row, col, RoomState.Fire)
                print(f"🔥 Fire added to R{floor}_{row}_{col}")
            else:
                print("Invalid room.")

if __name__ == '__main__':
    
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    
    # Building configuration
    FLOORS = 3
    ROWS = 3
    COLS = 4
    config = (FLOORS, ROWS, COLS)
    
    fire_spread_time = 1
    time_since_fire = 0
    tick_speed = 500  # Milliseconds per tick
    paused = False


    server = Server(config)

    # Assign 3D positions
    nodes = server.getNodes()
    pos = {node.name: (node.col, node.row, node.floor) for node in nodes}

    # Initialize person
    person = Person("R2_0_0", pos)

    # Start input thread (this can run in a separate thread)
    t1 = threading.Thread(target=inputThread, args=(server,))
    t1.start()

    # Run Matplotlib in the **main thread**
    displayThread(server, pos)  

    t1.join()  # Wait for input thread to finish
    print("Exiting program...")
