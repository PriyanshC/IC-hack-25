import random
from networkx import DiGraph
import networkx as nx

class Server:
    def __init__(self, config):
        self.FLOORS, self.ROWS, self.COLS = config
        self.config = config
        self.state = DiGraph()

        # Generate nodes
        self.nodes = [f"R{floor}_{row}_{col}" for floor in range(self.FLOORS) for row in range(self.ROWS) for col in range(self.COLS)]
        self.stairwell_row, self.stairwell_col = self.ROWS // 2, self.COLS // 2
        self.stairwell_nodes = {f"R{floor}_{self.stairwell_row}_{self.stairwell_col}" for floor in range(self.FLOORS)}
        self.exit_nodes = {f"R0_{random.randint(0, self.ROWS-1)}_{random.randint(0, self.COLS-1)}"}  # Random exit
        self.fire_nodes = set()
        
        self.constructGraph()



    # Set up graph connections
    def constructGraph(self):
        # Add nodes to graph
        for node in self.nodes:
            self.state.add_node(node, exit=node in self.exit_nodes, stairwell=node in self.stairwell_nodes)
        
        # Connect rooms within the same floor
        for floor in range(self.FLOORS):
            for row in range(self.ROWS):
                for col in range(self.COLS):
                    current = f"R{floor}_{row}_{col}"
                    if col < self.COLS - 1: self.state.add_edge(current, f"R{floor}_{row}_{col + 1}", weight=1)
                    if col > 0: self.state.add_edge(current, f"R{floor}_{row}_{col - 1}", weight=1)
                    if row < self.ROWS - 1: self.state.add_edge(current, f"R{floor}_{row + 1}_{col}", weight=1)
                    if row > 0: self.state.add_edge(current, f"R{floor}_{row - 1}_{col}", weight=1)

        # Connect floors via stairwell
        for floor in range(self.FLOORS - 1):
            lower, upper = f"R{floor}_{self.stairwell_row}_{self.stairwell_col}", f"R{floor + 1}_{self.stairwell_row}_{self.stairwell_col}"
            self.state.add_edge(lower, upper, weight=1)
            self.state.add_edge(upper, lower, weight=1)

    # Return the current state of the building (the graph)
    def pollState(self) -> DiGraph:
        return self.state

    # Update a room to be set on fire and recalculate routes
    def updateRoom(self, nodeName: int):
        node = self.state.nodes[nodeName]

        # self.fire_nodes.add(node.name)
        # node.setFire()

        self.calculateExitRoutes()

    # Function to find safest paths
    def calculateExitRoutes(self):
        safe_paths = {}
        for node in self.state.nodes:
            if node in self.exit_nodes:
                safe_paths[node] = None
                continue
            valid_paths = []
            for exit_node in self.exit_nodes:
                try:
                    paths = list(nx.all_simple_paths(self.state, source=node, target=exit_node))
                    for path in paths:
                        if all(n not in self.fire_nodes for n in path):
                            valid_paths.append(path)
                except nx.NetworkXNoPath:
                    continue
            safe_paths[node] = min(valid_paths, key=len) if valid_paths else None
            if not safe_paths[node]:
                # node.setBlocked()
                pass
            else:
                # node.safePath(safe_paths[node])
                pass