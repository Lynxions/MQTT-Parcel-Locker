import random
import string
from locker.Cell import Cell
from locker.Locker import Locker

locker = Locker(1, "broker.captechvn.com", 443)

locker.connect(60)

for i in range(1, 11):
    locker.add_cell(i)

message = '{"request":"open"}'
#json_string = msg.payload.decode("utf-8").replace("'", '"').replace("False", "false").replace("True", "true").replace("None", "null")

locker.publish("locker/1/cell/5", message, 0)

locker.loop_forever()
