import paho.mqtt.client as mqtt
import json
from .Cell import Cell, CELL_STATUS
from enum import Enum

class REQUEST(Enum):
    OPEN = "open"
    CLOSE = "close"
    PRINT_QR = "print_qr"

class UPDATE(Enum):
    OPENING = "opening"
    CLOSING = "closing"
    OCCUPIED = "occupied"
    EMPTY = "empty"

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

    def add_cell(self, cell_id: int):
        cell = Cell(cell_id)
        self.cells[cell_id] = cell

    def remove_cell(self, cell: Cell):
        del self.cells[cell.id]

    def get_cell(self, id) -> Cell:
        return self.cells[id]
    
    def get_empty_cells(self):
        return [cell for cell in self.cells.values() if not cell.occupied]
    
    def get_occupied_cells(self):
        return [cell for cell in self.cells.values() if cell.occupied]
    
    def update_status(self, cell_id, status: CELL_STATUS):
        self.cells[cell_id].status = status
        # self.publish(f"locker/{self.id}/cell/{cell_id}", f'"status": "{status.value}"', 0)

    def update_status_door(self, cell_id, status: CELL_STATUS):
        self.cells[cell_id].status_door = status

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        # self.publish(f"locker/{self.id}/cell/2", "1")

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            body = json.loads(msg.payload.decode("utf-8"))
            cell_id = topic.split("/")[-1]
            # Format body to json
            if "request" in body:
                request = body["request"]
                if request == REQUEST.OPEN.value:
                    self.open_cell(cell_id)
                elif request == REQUEST.PRINT_QR.value:
                    self.print_QR_code(body["order_id"], body["OTP"])
                elif request == REQUEST.CLOSE.value:
                    self.close_cell(cell_id)
            elif "update" in body:
                update = body["update"]
                if update == UPDATE.OPENING.value:
                    self.update_status_door(cell_id, UPDATE.OPENING)
                elif update == UPDATE.CLOSING.value:
                    self.update_status_door(cell_id, UPDATE.CLOSING)
            else:
                request = "None"

            print(f"Received message: {cell_id} {request}")
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")

    def on_subscribe(self, client, userdata, mid, reason_code, properties):
        print(f"Locker subscribed: {self.id}")

    def connect(self, keepalive):
        if self.host is None or self.port is None:
            raise Exception("Host and port must be set")
        super().connect(self.host, self.port, keepalive)
        self.subscribe(f"locker/{self.id}/cell/#")
        self.subscribe("rpi/locker/#")

    def open_cell(self, cell_id):
        cell = self.get_cell(int(cell_id))
        self.publish(f"rpi/locker/{cell_id}", '{"cell":"on"}', 0)
        if cell.status == CELL_STATUS.OCCUPIED:
            self.update_status(int(cell_id), False) #False?
        else:
            print("Cell is empty")
    
    def close_cell(self, cell_id):
        cell = self.get_cell(int(cell_id))
        self.publish(f"rpi/locker/{cell_id}", '{"cell":"off"}', 0)
        if cell.status == CELL_STATUS.OCCUPIED:
            print("Cell is occupied")
        else:
            self.update_status(int(cell_id), True)
    
    def print_QR_code(self, order_id, OTP):
        # TODO: Implement this function
        pass
