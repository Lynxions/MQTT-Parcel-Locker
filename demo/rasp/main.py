from locker.Locker import Locker
import tkinter as tk

from locker.QR import QRCodeGeneratorApp
# Read environment variables
from decouple import config

root = tk.Tk()
app = QRCodeGeneratorApp(root)

MQTT_HOST = config("MQTT_HOST")
MQTT_PORT = int(config("MQTT_PORT"))

HTTP_HOST = config("HTTP_HOST")
HTTP_PORT = int(config("HTTP_PORT"))
IS_HTTPS = config("IS_HTTPS")

ID = config("ID")
if IS_HTTPS == "True":
    IS_HTTPS = True
else:
    IS_HTTPS = False

locker = Locker(2, MQTT_HOST, MQTT_PORT, app.generate_qr_code, app.display_sucess)
print(MQTT_HOST, MQTT_PORT)
locker.connect(60)
locker.connect_to_http(HTTP_HOST, HTTP_PORT, IS_HTTPS)

locker.loop_start()
root.mainloop()    # You can directly call the function with order_id and otp5
