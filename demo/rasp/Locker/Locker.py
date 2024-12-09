import paho.mqtt.client as mqtt
import json
from .Cell import Cell, CELL_STATUS
from enum import Enum
import http.client

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
    id: str
    cells: dict
    host: str
    port: int
    cells_mapping: dict

    def __init__(self, id, host, port, on_generate_qr, display_sucess):
        super().__init__(mqtt.CallbackAPIVersion.VERSION2)
        self.id = id
        self.host = host
        self.port = int(port)
        self.cells = {}
        self.on_gernerate_qr = on_generate_qr
        self.display_sucess = display_sucess
        self.cells_mapping = {}

    def add_cell(self, cell_id: str):
        cell = Cell(cell_id)
        self.cells_mapping[cell_id] = len(self.cells_mapping) + 1
        self.cells[cell_id] = cell
        print(f"Added cell {cell_id} with status {cell.status}")

    def connect_to_http(self, host, port, is_https=False):
        # GET request to http_host
        
        assert self.id is not None
        assert port is not None
        assert host is not None

        if is_https:
            conn = http.client.HTTPSConnection(host, port)
        else:
            conn = http.client.HTTPConnection(host, port)
        
        conn.request("GET", f"/api/v1/lockers/{self.id}/cells")
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        print(data)
        for cell in json.loads(data):
            self.add_cell(cell["cell_id"])
            # self.update_status(cell["cell_id"], CELL_STATUS(cell["occupied"]))
        
    def remove_cell(self, cell: Cell):
        del self.cells[cell.id]

    def get_cell(self, id) -> Cell:
        if id in self.cells:
            return self.cells[id]
        else:
            raise KeyError(f"Cell with id {id} not found")
        
    def get_empty_cells(self):
        return [cell for cell in self.cells.values() if cell.status == CELL_STATUS.EMPTY]

    def get_occupied_cells(self):
        return [cell for cell in self.cells.values() if cell.status == CELL_STATUS.OCCUPIED]

    def update_status(self, cell_id, status: CELL_STATUS):
        if cell_id in self.cells:
            self.cells[cell_id].status = status
            self.publish(f"locker/{self.id}/cell/{cell_id}", f'"status": "{status.value}"', 0)
        else:
            print(f"Cell with id {cell_id} does not exist")

    def update_status_door(self, cell_id, status):
        if cell_id in self.cells:
            self.cells[cell_id].status_door = status
        else:
            print(f"Cell with id {cell_id} does not exist")

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        #self.publish(f"locker/{self.id}/cell/2", "1")

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            # Attempt to decode JSON, handle non-dict bodies
            try:
                body = json.loads(msg.payload.decode("utf-8"))
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}. Raw message: {msg.payload}")
                return

            # Check if the body is a dictionary before proceeding
            if not isinstance(body, dict):
                print(f"Unexpected message format: {body}. Expected a dictionary.")
                return
            
            # Extract the cell_id from the topic
            cell_id = topic.split("/")[-1]
            print(f"Message received for cell {cell_id}: {body}")
   
            # Format body to json
            if "request" in body:
                request = body["request"]
                if request == REQUEST.OPEN.value:
                    self.open_cell(cell_id)
                    self.display_sucess(self.cells_mapping[cell_id])
                elif request == REQUEST.PRINT_QR.value:
                    self.on_gernerate_qr(body["order_id"], body["OTP"])
                elif request == REQUEST.CLOSE.value:
                    self.close_cell(cell_id)
            elif "update" in body:
                update = body["update"]
                if update == UPDATE.OPENING.value:
                    self.update_status_door(cell_id, UPDATE.OPENING)
                elif update == UPDATE.CLOSING.value:
                    self.update_status_door(cell_id, UPDATE.CLOSING)
            else:
                print(f"Unknown request for cell {cell_id}, request: {body}")

            # print(f"Received message: {cell_id} {request}")
        except KeyError as e:
            print(f"KeyError: {e}. Available cells: {list(self.cells.keys())}")
        except ValueError as e:
            print(f"ValueError: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def on_subscribe(self, client, userdata, mid, reason_code, properties):
        print(f"Locker subscribed: {self.id}")

    def connect(self, keepalive):
        if self.host is None or self.port is None:
            raise Exception("Host and port must be set")
        super().connect(self.host, self.port, keepalive)
        # self.subscribe(f"locker/{self.id}/cell/#")
        self.subscribe(f"locker/{self.id}/#")
        # self.subscribe("rpi/locker/#")

    def open_cell(self, cell_id):
        try:
            cell = self.get_cell(cell_id)
            #self.publish(f"rpi/locker/{cell_id}", '{"cell":"on"}', 0)
            cell_id_mapping = self.cells_mapping[cell_id]
            #print(cell_id_mapping)
            #self.publish(f"rpi/locker{cell_id_mapping}", '{"cell":"on"}', 0)
            cell.connect_broker(cell_id_mapping)
            if cell.status == CELL_STATUS.OCCUPIED: 
                self.update_status(cell_id, CELL_STATUS.EMPTY)  # Updating to empty if occupied
            else:
                print(f"Cell {cell_id} is already empty")
        except KeyError as e:
            print(e)

    def close_cell(self, cell_id):
        try:
            cell = self.get_cell(cell_id)
            #self.publish(f"rpi/locker/{cell_id}", '{"cell":"off"}', 0)
            cell_id_mapping = self.cells_mapping[cell_id]
            print(cell_id_mapping)
            self.publish(f"rpi/locker{cell_id_mapping}", '{"cell":"off"}', 0)
            if cell.status == CELL_STATUS.OCCUPIED:
                print(f"Cell {cell_id} is occupied")
            else:
                self.update_status(cell_id, CELL_STATUS.OCCUPIED)  # Updating to occupied if empty
        except KeyError as e:
            print(e)
