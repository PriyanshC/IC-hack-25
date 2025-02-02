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
            self.state.add_node(node.name, exit=node in self.exit_nodes, fire=False, stairwell=node in self.stairwell_nodes, warning=float('inf'), distance_to_safety=float('inf'))
        
        # print("State", self.state)

        # Connect rooms within the same floor
        for floor in range(self.FLOORS):
            for row in range(self.ROWS):
                for col in range(self.COLS):
                    current = self.findIndex(floor, row, col)
                    if col < self.COLS - 1: self.state.add_edge(current.name, self.findIndex(floor, row, col + 1).name, weight=1)
                    if col > 0: self.state.add_edge(current.name, self.findIndex(floor, row, col - 1).name, weight=1)
                    if row < self.ROWS - 1: self.state.add_edge(current.name, self.findIndex(floor, row + 1, col).name, weight=1)
                    if row > 0: self.state.add_edge(current.name, self.findIndex(floor, row - 1, col).name, weight=1)

        # Connect floors via stairwell
        for floor in range(self.FLOORS - 1):
            lower, upper = self.findIndex(floor, self.stairwell_row, self.stairwell_col).name, self.findIndex(floor + 1, self.stairwell_row, self.stairwell_col).name
            self.state.add_edge(lower, upper, weight=1)
            self.state.add_edge(upper, lower, weight=1)

    # Return the current state of the building (the graph)
    def pollState(self) -> DiGraph:
        return self.state

    # Update a room to be set on fire and recalculate routes
    def updateRoom(self, floor, row, col, type):

        node = self.findIndex(floor, row, col)
        self.fire_nodes.add(node)
        if type == RoomState.Fire:
            self.state.nodes[node.name]["fire"] = True
            node.setState(RoomState.Fire)
        if type == RoomState.Hurry:
            node.setState(RoomState.Hurry)
        if type == RoomState.Trap:
            node.setState(RoomState.Trap)


        self.calculateExitRoutes()
        
        
        # Function to find safest paths

        

    # Function to find safest paths
    def calculateExitRoutes(self):
        safe_paths = {}
        blocked_paths = set()
        
        for node in self.nodes:
            if node in self.exit_nodes:
                safe_paths[node.name] = None
                continue
            
            valid_paths = []
            for exit_node in self.exit_nodes:
                try:
                    # Generate all simple paths from the current node to the exit node
                    paths = list(nx.all_simple_paths(self.state, source=node.name, target=exit_node.name))
                    
                    # Filter paths to exclude those that go through fire nodes
                    for path in paths:
                        if all(not self.state.nodes[n]["fire"] for n in path):
                            valid_paths.append(path)
                except nx.NetworkXNoPath:
                    continue
            
            # Choose the shortest valid path if any exist
            if valid_paths:
                safe_paths[node.name] = min(valid_paths, key=len)
            else:
                safe_paths[node.name] = None
                blocked_paths.add(node)
                node.setState(RoomState.Trap)

        return safe_paths, blocked_paths