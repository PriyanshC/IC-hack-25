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
    print()
    print(server.fire_nodes)
    print()
    for node in server.fire_nodes:
        floor, row, col = node.floor, node.row, node.col
        neighbors = []
        if row != 0:
            neighbors.append(server.findIndex(floor, row-1, col))
        elif row != server.ROWS - 1:
            neighbors.append(server.findIndex(floor, row+1, col))
        elif col != 0:
            neighbors.append(server.findIndex(floor, row, col-1))
        elif col != server.COL - 1:
            neighbors.append(server.findIndex(floor, row, col+1))
        
        if node in server.stairwell_nodes and floor < server.FLOORS - 1:
            neighbors.append(server.findIndex(floor+1, row, col))
        if node in server.stairwell_nodes and floor > 0:
            neighbors.append(server.findIndex(floor-1, row, col))

        print("NEIGHBOURS")
        print(neighbors)
        print("NEIGHBOURS")
        
        # Filter neighbors that are not on fire yet
        uninfected_neighbors = [n for n in neighbors if n not in server.fire_nodes]
        
        print(uninfected_neighbors)
        # If there are any uninfected neighbors, randomly pick one to infect
        if uninfected_neighbors:
            new_fire_node = random.choice(uninfected_neighbors)
            if new_fire_node not in server.exit_nodes:
                new_fire_nodes.add(new_fire_node)

        print("NEW FIRE NODE JUST DROPPED")
        print(new_fire_nodes)
        print("LOLOLOLOLOLOL")

    
    # Update fire nodes
    for node in new_fire_nodes:
        server.updateRoom(node.floor, node.row, node.col)


# 3D Visualization
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection="3d")

def updateGraph(frame, server, pos):
    print("HALLO")
    ax.clear()
    G = server.pollState()
    nodes = server.getNodes()   
    spread_fire(server)  # Fix: Pass server argument
    safe_paths, blocked_nodes = server.calculateExitRoutes()
    
    node_colors = [
        "red" if G.nodes[node.name]["fire"] else
        "blue" if G.nodes[node.name]["exit"] else
        "orange" if node in blocked_nodes else
        "green" for node in nodes
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
    
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    ax.set_zlabel("Floor")
    ax.set_title(f"Time Step: {frame+1}")

def displayThread(server, pos):
    ani = FuncAnimation(fig, updateGraph, fargs=(server, pos), interval=3000)
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
                server.updateRoom(floor, row, col)
                print(f"🔥 Fire added to R{floor}_{row}_{col}")
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
    nodes = server.getNodes()
    pos = {node.name: (node.col, node.row, node.floor) for node in nodes}

    # Start input thread (this can run in a separate thread)
    t1 = threading.Thread(target=inputThread, args=(server,))
    t1.start()

    # Run Matplotlib in the **main thread**
    displayThread(server, pos)  

    t1.join()  # Wait for input thread to finish
    print("Exiting program...")
