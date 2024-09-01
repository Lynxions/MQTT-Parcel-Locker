class Cell:
    id: int
    occupied: bool
    def __init__(self, id):
        self.id = id
        self.occupied = False