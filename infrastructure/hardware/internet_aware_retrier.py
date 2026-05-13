import tkinter as tk
from tkinter import ttk

from infrastructure.observability.logger import Logger


class InternetAwareRetryer:
    root_app = None
    popup = None

    @staticmethod
    def start(func: callable):
        try:
            func()

            if InternetAwareRetryer.root_app is not None and InternetAwareRetryer.popup is not None:
                InternetAwareRetryer.popup.destroy()
                InternetAwareRetryer.popup = None
        except Exception as e:
            Logger.get_logger().warning(f"InternetAwareRetryer caught: {e}")

            if InternetAwareRetryer.root_app is not None and InternetAwareRetryer.popup is None:
                popup = tk.Toplevel(InternetAwareRetryer.root_app)
                popup.title("Connection Error")
                popup.geometry("300x120")
                popup.resizable(False, False)

                label = ttk.Label(popup, text="No internet connection detected!", wraplength=250)
                label.pack(pady=20)

                popup.attributes("-topmost", True)
                InternetAwareRetryer.popup = popup

            if InternetAwareRetryer.root_app is not None:
                InternetAwareRetryer.root_app.after(5000, lambda: InternetAwareRetryer.start(func))
