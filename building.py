from enum import Enum
import random

class RoomState(Enum):
    Fire = 1
    Trap = 2
    Safe = 3
    Exit = 4

    def color(self) -> str:
        match self:
            case RoomState.Fire: 
                return "indianred"
            
            case RoomState.Trap: 
                return "orange"
            
            case RoomState.Safe: 
                return "lightblue"

            case RoomState.Exit: 
                return "lightgreen"


class Room:
    def __init__(self, floor, row, col):
        self.floor = floor
        self.row = row
        self.col = col
        self.state = RoomState.Safe

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col and self.state == other.state and self.floor == other.floor

    def __hash__(self):
        return hash((self.row, self.col, self.state, self.floor))

    def name(self) -> str:
        return f"{self.floor}-{self.row}-{self.col}"

    def color(self) -> str:
        return self.state.color()

    def setState(self, newState: RoomState): 
        self.state = newState

    
# class Door:
#     def __init__(self, prev: Room, next: Room):
#         self.prev = prev
#         self.next = next
#
#     def color(self):
#         return self.next.color()
#
#
# class Building:
#     def __init__(self, roomsPerFloor: list[int], stairsPerFloor: list[int], exits: int, exitsOnlyOnGround: bool = True):
#         self.rooms = [[Room(f, r) for r in range(1, roomsPerFloor[f] + 1)] for f in range(len(roomsPerFloor))]
#         self.doors: list[Door] = []
#
#         for f, floor in enumerate(self.rooms):
#             if f > 0:
#                 indices = [i for i in range(len(floor))]
#                 random.shuffle(indices)
#
#                 for s in indices[: stairsPerFloor[f - 1]]:
#                     self.doors.append(Door(floor[s], self.rooms[f - 1][s]))
#
#
#             for prev_room in range(len(self.rooms[f]) - 1):
#                 for next_room in range(len(self.rooms[f])):
#                     self.doors.append(Door(self.rooms[f][prev_room], self.rooms[f][next_room]))
#
#
#         if exitsOnlyOnGround:
#             indices = [i for i in range(len(self.rooms[0]))]
#             random.shuffle(indices)
#
#             [self.rooms[0][i].setState(RoomState.Exit) for i in indices[: exits]]
#
#
#         # Choose room to start fire
#         f = random.randrange(0, len(self.rooms))
#         r = random.randrange(0, len(self.rooms[f]))
#
#         self.rooms[f][r].setState(RoomState.Fire)
#
#
#     def balanced(floors: int, roomsPerFloor: int, exits: int, exitsOnlyOnGround: bool = True):
#         return Building([roomsPerFloor for _ in range(floors)], exits, exitsOnlyOnGround)
#