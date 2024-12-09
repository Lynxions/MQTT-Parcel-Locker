import paho.mqtt.client as mqtt
from enum import Enum

MQTT_BROKER = "10.238.60.250"
MQTT_PORT = 1883

class CELL_STATUS(Enum):
    OPENING = "opening"
    EMPTY = "empty"
    OCCUPIED = "occupied"

class CELL_DOOR_STATUS(Enum):
    OPENING = "opening"
    CLOSING = "closing"

class Cell:
    id: str
    status: CELL_STATUS
    status_door: CELL_DOOR_STATUS

    def __init__(self, id):
        self.id = id
        self.status = CELL_STATUS.EMPTY
        self.status_door = CELL_DOOR_STATUS.OPENING
        
    def connect_broker(self, cells_mapping_id):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        client.publish(f"rpi/locker{cells_mapping_id}", '{"cell":"on"}', 0)
        client.loop_start()
        client.disconnect()
