import random
import string
from locker.Cell import Cell
from locker.Locker import Locker
import tkinter as tk

from locker.QR import QRCodeGeneratorApp

root = tk.Tk()
app = QRCodeGeneratorApp(root)

locker = Locker(1, "broker.captechvn.com", 443, app.generate_qr_code)

locker.connect(60)

for i in range(1, 11):
    locker.add_cell(i)


# message = '{"request":"open"}'
#json_string = msg.payload.decode("utf-8").replace("'", '"').replace("False", "false").replace("True", "true").replace("None", "null")

# locker.publish("locker/1/cell/5", message, 0)

locker.loop_start()
root.mainloop()    # You can directly call the function with order_id and otp