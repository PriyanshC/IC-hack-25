import random
from networkx import DiGraph
import networkx as nx
from building import Room
from building import RoomState

class Server:
    def __init__(self, config):
        self.FLOORS, self.ROWS, self.COLS = config
        self.config = config
        self.state = DiGraph()

        # Generate nodes
        self.nodes = [Room(floor, row, col) for floor in range(self.FLOORS) for row in range(self.ROWS) for col in range(self.COLS)]
        self.stairwell_row, self.stairwell_col = self.ROWS // 2, self.COLS // 2
        self.stairwell_nodes = {self.findIndex(floor, self.stairwell_row, self.stairwell_col) for floor in range(self.FLOORS)}
        self.exit_nodes = {self.findIndex(0, random.randint(0, self.ROWS-1), random.randint(0, self.COLS-1))} # Random exit
        self.fire_nodes = set()
        
        self.constructGraph()

    def getNodes(self):
        return self.nodes

    def findIndex(self, floor, row, col):
        return self.nodes[floor * (self.ROWS * self.COLS) + row * self.COLS + col]

    # Set up graph connections
    def constructGraph(self):
        # Add nodes to graph
        # print(len(self.nodes))
        for node in self.nodes:
            self.state.add_node(node.name, exit=node in self.exit_nodes, fire=False, stairwell=node in self.stairwell_nodes)
        
        # print("State", self.state)

        # Connect rooms within the same floor
        for floor in range(self.FLOORS):
            for row in range(self.ROWS):
                for col in range(self.COLS):
                    current = self.findIndex(floor, row, col)
                    if col < self.COLS - 1: self.state.add_edge(current, self.findIndex(floor, row, col + 1), weight=1)
                    if col > 0: self.state.add_edge(current, self.findIndex(floor, row, col - 1), weight=1)
                    if row < self.ROWS - 1: self.state.add_edge(current, self.findIndex(floor, row + 1, col), weight=1)
                    if row > 0: self.state.add_edge(current, self.findIndex(floor, row - 1, col), weight=1)

        # Connect floors via stairwell
        for floor in range(self.FLOORS - 1):
            lower, upper = self.findIndex(floor, self.stairwell_row, self.stairwell_col), self.findIndex(floor + 1, self.stairwell_row, self.stairwell_col)
            self.state.add_edge(lower, upper, weight=1)
            self.state.add_edge(upper, lower, weight=1)

    # Return the current state of the building (the graph)
    def pollState(self) -> DiGraph:
        return self.state

    # Update a room to be set on fire and recalculate routes
    def updateRoom(self, floor, row, col):

        node = self.findIndex(floor, row, col)

        self.fire_nodes.add(node)
        print(self.state.nodes)
        self.state.nodes[node.name]["fire"] = True
        node.setState(RoomState.Fire)

        self.calculateExitRoutes()

    # Function to find safest paths
    def calculateExitRoutes(self):
        safe_paths = {}
        blocked_paths = set()
        for node in self.nodes:
            if node in self.exit_nodes:
                safe_paths[node] = None
                continue
            valid_paths = []
            for exit_node in self.exit_nodes:
                try:
                    paths = list(nx.all_simple_paths(self.state, source=node.name, target=exit_node.name))
                    for path in paths:
                        if all(n not in self.fire_nodes for n in path):
                            valid_paths.append(path)
                except nx.NetworkXNoPath:
                    continue
            safe_paths[node] = min(valid_paths, key=len) if valid_paths else None
            if not safe_paths[node]:
                blocked_paths.add(node)
                # node.setBlocked()
                pass
            else:
                # node.safePath(safe_paths[node])
                pass

        return safe_paths, blocked_paths