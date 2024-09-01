from locker.Cell import Cell
from locker.Locker import Locker

locker = Locker(1, "broker.captechvn.com", 443)


locker.connect(60)
for i in range(1, 11):
    locker.add_cell(Cell(i))
    
locker.loop_forever()
