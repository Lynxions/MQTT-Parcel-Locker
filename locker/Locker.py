import paho.mqtt.client as mqtt
import json
from locker import Cell

class Locker(mqtt.Client):
    id: int
    cells: dict
    host: str
    port: int

    def __init__(self, id, host, port):
        super().__init__(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
        self.id = id
        self.host = host
        self.port = port
        self.cells = {}
        self.tls_set()


    def add_cell(self, cell: Cell):
        self.cells[cell.id] = cell

    def remove_cell(self, cell: Cell):
        del self.cells[cell.id]

    def get_cell(self, id):
        return self.cells[id]
    
    def get_empty_cells(self):
        return [cell for cell in self.cells.values() if not cell.occupied]
    
    def get_occupied_cells(self):
        return [cell for cell in self.cells.values() if cell.occupied]
    
    def update_occuiped(self, cell_id, occupied: bool):
        self.cells[cell_id].occupied = occupied
        self.publish(f"locker/{self.id}/cell/{cell_id}", {
            "occupied": occupied
        })

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        # self.publish(f"locker/{self.id}/cell/2", "1")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        body = json.loads(msg.payload.decode("utf-8"))
        cell_id = topic.split("/")[-1]
        # Format body to json
        request = body["request"]
        print(f"Received message: {cell_id} {request}")

    def on_subscribe(self, client, userdata, mid, reason_code, properties):
        print(f"Locker subscribed: {self.id}")

    def on_publish(self, client, userdata, mid, reason_code, properties):
        print(f"published: {mid}")

    def connect(self, keepalive):
        if self.host is None or self.port is None:
            raise Exception("Host and port must be set")
        super().connect(self.host, self.port, keepalive)
        self.subscribe(f"locker/{self.id}/cell/#")
