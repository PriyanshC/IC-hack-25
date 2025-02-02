from enum import Enum
import random

class RoomState(Enum):
    Fire = 1
    Trap = 2
    Safe = 3
    Exit = 4
    Hurry = 5



class Room:
    def __init__(self, floor, row, col):
        self.floor = floor
        self.row = row
        self.col = col
        self.name = f"R{floor}_{row}_{col}"
        self.state = RoomState.Safe

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col and self.floor == other.floor

    def __hash__(self):
        return hash(repr(self))
    
    def __repr__(self):
        return f"Room({self.floor}, {self.row}, {self.col})"

    def __str__(self):
        return f"Room({self.floor}, {self.row}, {self.col})"

    def name(self) -> str:
        return self.name

    def setState(self, newState: RoomState): 
        self.state = newState

    
