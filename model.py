import math
import networkx as nx

from building import Building, Room, Door


class Model:
    def __init__(self, building: Building):
        self.building = building
        
    def graph(self) -> nx.DiGraph:
        # Define the building as a graph
        graph = nx.DiGraph()
        
        # Add nodes to graph
        [[graph.add_node(room, label=room.name(), color=room.color()) for room in floor] for floor in self.building.rooms]
        [graph.add_edge(door.prev, door.next) for door in self.building.doors]

        return graph
    
    def plot(self, axes):
        # Draw nodes on axes
        pos: dict[Room, tuple[int, int, int]] = {}
        
        for f, floor in enumerate(self.building.rooms):
            sq = math.sqrt(len(floor))  

            for r, room in enumerate(floor):
                x = r % sq
                y = (r - x) // sq

                pos[room] = (x, y, f)

        for room, (x, y, z) in pos.items():
            axes.scatter(x, y, z, color=room.color(), s=200)

        for door in self.building.doors:
            xs, ys, zs = zip(*[pos[door.prev], pos[door.next]])
            axes.plot(xs, ys, zs, door.color())