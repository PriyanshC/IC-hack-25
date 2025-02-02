import networkx as nx
import matplotlib.pyplot as plt
import random
import time
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation


# # Fire spread function
# def spread_fire():
#     new_fire_nodes = set()
#     for node in fire_nodes:
#         floor, row, col = map(int, node[1:].split("_"))
#         neighbors = [
#             f"R{floor}_{row+1}_{col}", f"R{floor}_{row-1}_{col}",
#             f"R{floor}_{row}_{col+1}", f"R{floor}_{row}_{col-1}"
#         ]
#         if node in stairwell_nodes and floor < FLOORS - 1:
#             neighbors.append(f"R{floor+1}_{row}_{col}")
#         if node in stairwell_nodes and floor > 0:
#             neighbors.append(f"R{floor-1}_{row}_{col}")
        
#         # Filter neighbors that are not on fire yet
#         uninfected_neighbors = [n for n in neighbors if n not in fire_nodes and n in G.nodes]
        
#         # If there are any uninfected neighbors, randomly pick one to infect
#         if uninfected_neighbors:
#             new_fire_node = random.choice(uninfected_neighbors)
#             if new_fire_node not in exit_nodes:
#                 new_fire_nodes.add(new_fire_node)
    
#     # Update fire nodes
#     fire_nodes.update(new_fire_nodes)
#     for node in fire_nodes:
#         G.nodes[node]["fire"] = True


# # 3D Visualization
# fig = plt.figure(figsize=(10, 7))
# ax = fig.add_subplot(111, projection="3d")

# # Assign 3D positions
# pos = {node: (int(node.split("_")[2]), int(node.split("_")[1]), int(node.split("_")[0][1:])) for node in G.nodes}

# def update(frame):
#     ax.clear()
#     spread_fire()
#     safe_paths, blocked_nodes = find_safest_paths(G, exit_nodes)
    
#     node_colors = [
#         "red" if G.nodes[n]["fire"] else
#         "blue" if G.nodes[n]["exit"] else
#         "orange" if n in blocked_nodes else
#         "green" for n in G.nodes
#     ]
    
#     for node, (x, y, z) in pos.items():
#         ax.scatter(x, y, z, color=node_colors[list(G.nodes).index(node)], s=200)
    
#     for edge in G.edges:
#         x_vals, y_vals, z_vals = zip(*[pos[edge[0]], pos[edge[1]]])
#         ax.plot(x_vals, y_vals, z_vals, "gray")
    
#     for node, path in safe_paths.items():
#         if path and len(path) > 1:
#             for i in range(len(path) - 1):
#                 x_vals, y_vals, z_vals = zip(*[pos[path[i]], pos[path[i+1]]])
#                 ax.plot(x_vals, y_vals, z_vals, "blue", linewidth=2)
    
#     ax.set_xlabel("Column")
#     ax.set_ylabel("Row")
#     ax.set_zlabel("Floor")
#     ax.set_title(f"Time Step: {frame+1}")

# ani = FuncAnimation(fig, update, frames=1, interval=3000)
# plt.show()


'''
1: server needs to hold state/layout of building
2: server receives data from nodes to update snapshot (node on fire let server know)
3: server needs to calculate fastest way out for every possible safe (safe is when there is a valid escape path)
4: server lets the blocked nodes know theyre blocked (orange)
'''
from server import Server 

def startFire(server):
    nodes = list(server.pollState().nodes())

    # sake of setting a fire
    fire_nodes = random.sample(nodes, 1)   # Start with 1 fire nodes
    
    for fire_node in fire_nodes:
        server.updateRoom(fire_node)


def main():
    # Building configuration
    FLOORS = 3
    ROWS = 3
    COLS = 4
    config = (FLOORS, ROWS, COLS)

    server = Server(config)

    startFire(server)


if __name__ == '__main__':
    main()