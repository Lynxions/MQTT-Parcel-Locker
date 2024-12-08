import tkinter as tk
from tkinter import messagebox
import qrcode
from PIL import Image, ImageTk

class QRCodeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")

        # Image display area
        self.canvas = tk.Canvas(root, width=400, height=300)
        self.canvas.pack(pady=10)

        self.qr_image = None
        
        self.root.attributes('-fullscreen', True)

    def generate_qr_code(self, order_id, otp):
        try:
            # QR code content
            qr_data = f'{{"order_id": "{order_id}", "otp": "{otp}"}}'

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            self.qr_image = qr.make_image(fill='black', back_color='white')

            # Display QR code on canvas
            self.display_qr_code(order_id)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR Code: {str(e)}")

    def display_qr_code(self, msg):
        if self.qr_image is not None:
            # Convert the QR code image to a format that Tkinter can display
            qr_pil_image = self.qr_image.convert('RGB')
            qr_tk_image = ImageTk.PhotoImage(qr_pil_image)

            # Display the image on the canvas
            self.canvas.create_image(200, 150, image=qr_tk_image)
            self.canvas.image = qr_tk_image  # Keep reference to prevent garbage collection

            self.canvas.create_text(200, 100, text=msg, fill="black", font=("Arial", 16))
 #if __name__ == "__main__":
 #    root = tk.Tk()
 #    app = QRCodeGeneratorApp(root)

     # You can directly call the function with order_id and otp
 #    order_id = "11"
 #    otp = "123123"
 #    app.generate_qr_code(order_id, otp)

#     root.mainloop()
