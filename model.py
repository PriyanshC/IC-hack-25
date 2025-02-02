import math
import networkx as nx

from building import Building, Room, Door, RoomState


class Model:
    def __init__(self, building: Building):
        self.building = building
        
    def graph(self) -> nx.DiGraph:
        # Define the building as a graph
        graph = nx.DiGraph()
        
        # Add nodes to graph
        [[graph.add_node(room) for room in floor] for floor in self.building.rooms]
        [graph.add_edge(door.prev, door.next) for door in self.building.doors]

        return graph
            
    # Function to find safest paths
    def updateStates(self):
        graph: nx.DiGraph = self.graph()
        exits = [node for node in graph.nodes if node.state == RoomState.Exit]
        
        for node in graph.nodes:
            if node.state == RoomState.Exit or node.state == RoomState.Fire:
                continue
            
            if len(exits) == 0:
                node.setState(RoomState.Trap)

            else:
                for exitNode in exits:
                    try:
                        paths = list(nx.all_simple_paths(graph, source=node, target=exitNode))
                        if any(all(n.state != RoomState.Fire for n in p) for p in paths):
                            node.setState(RoomState.Safe)

                        else:
                            node.setState(RoomState.Trap)

                    except nx.NetworkXNoPath:
                        node.setState(RoomState.Trap)

    
    def plot(self, axes):
        self.updateStates()

        # Draw nodes on axes
        pos: dict[Room, tuple[int, int, int]] = {}
        
        for f, floor in enumerate(self.building.rooms):
            sq = math.sqrt(len(floor))  

            for r, room in enumerate(floor):
                x = r % sq
                y = (r - x) // sq

                pos[room] = (x, y, f)

        for room, (x, y, z) in pos.items():
            axes.scatter(x, y, z, label=room.name(), color=room.color(), s=200)

        for door in self.building.doors:
            xs, ys, zs = zip(*[pos[door.prev], pos[door.next]])
            axes.plot(xs, ys, zs, door.color())