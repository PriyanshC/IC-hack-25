import threading
import networkx as nx
import matplotlib.pyplot as plt
import random
import time
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from server import Server

# Fire spread function
def spread_fire(server):
    new_fire_nodes = set()
    for node in server.fire_nodes:
        floor, row, col = map(int, node[1:].split("_"))
        neighbors = [
            f"R{floor}_{row+1}_{col}", f"R{floor}_{row-1}_{col}",
            f"R{floor}_{row}_{col+1}", f"R{floor}_{row}_{col-1}"
        ]
        if node in server.stairwell_nodes and floor < server.FLOORS - 1:
            neighbors.append(f"R{floor+1}_{row}_{col}")
        if node in server.stairwell_nodes and floor > 0:
            neighbors.append(f"R{floor-1}_{row}_{col}")
        
        # Filter neighbors that are not on fire yet
        uninfected_neighbors = [n for n in neighbors if n not in server.fire_nodes and n in server.pollState().nodes]
        
        # If there are any uninfected neighbors, randomly pick one to infect
        if uninfected_neighbors:
            new_fire_node = random.choice(uninfected_neighbors)
            if new_fire_node not in server.exit_nodes:
                new_fire_nodes.add(new_fire_node)
    
    # Update fire nodes
    server.fire_nodes.update(new_fire_nodes)
    for node in server.fire_nodes:
        server.pollState().nodes[node]["fire"] = True

# 3D Visualization
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection="3d")

def updateGraph(frame, server, pos):
    ax.clear()
    G = server.pollState()
    spread_fire(server)  # Fix: Pass server argument
    safe_paths, blocked_nodes = server.calculateExitRoutes()
    
    node_colors = [
        # "red" if G.nodes[n]["fire"] else
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

def displayThread(server, pos):
    ani = FuncAnimation(fig, updateGraph, frames=1, fargs=(server, pos), interval=3000)
    plt.show()

def inputThread(server):
    while True:
        user_input = input("Enter command (fire ROOM / exit): ").strip()
        if user_input == "exit":
            break
        elif user_input.startswith("fire "):
            room = user_input.split()[1]
            if room in server.pollState().nodes:
                server.updateRoom(room)
                print(f"🔥 Fire added to {room}")
            else:
                print("Invalid room.")

if __name__ == '__main__':
    
    # Building configuration
    FLOORS = 3
    ROWS = 3
    COLS = 4
    config = (FLOORS, ROWS, COLS)

    server = Server(config)

    # Assign 3D positions
    pos = {node: (int(node.split("_")[2]), int(node.split("_")[1]), int(node.split("_")[0][1:])) for node in server.pollState().nodes}

    # Start input thread (this can run in a separate thread)
    t1 = threading.Thread(target=inputThread, args=(server,))
    t1.start()

    # Run Matplotlib in the **main thread**
    displayThread(server, pos)  

    t1.join()  # Wait for input thread to finish
    print("Exiting program...")
