from enum import Enum

class CELL_STATUS(Enum):
    OPENNING = "openning"
    EMPTY = "empty"
    OCCUPIED = "occupied"

class Cell:
    id: int
    status: CELL_STATUS

    def __init__(self, id):
        self.id = id
        self.status = CELL_STATUS.EMPTY