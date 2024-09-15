from enum import Enum

class CELL_STATUS(Enum):
    OPENING = "opening"
    EMPTY = "empty"
    OCCUPIED = "occupied"

class CELL_DOOR_STATUS(Enum):
    OPENING = "opening"
    CLOSING = "closing"

class Cell:
    id: int
    status: CELL_STATUS
    status_door: CELL_DOOR_STATUS

    def __init__(self, id):
        self.id = id
        self.status = CELL_STATUS.EMPTY
        self.status_door = CELL_DOOR_STATUS.OPENING
