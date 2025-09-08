import tk
from tkinter import ttk


class InternetAwareRetryer:
    root_app = None
    popup = None

    @staticmethod
    def start(func: callable):
        try:
            raise Exception("teste")
            func()

            if InternetAwareRetryer.root_app is not None:
                InternetAwareRetryer.destroy()
                popup = None
        except Exception:
            if InternetAwareRetryer.root_app is None:
                popup = tk.Toplevel(InternetAwareRetryer.root_app)
                popup.title("Connection Error")
                popup.geometry("300x120")
                popup.resizable(False, False)

                label = ttk.Label(popup, text="⚠️ No internet connection detected!", wraplength=250)
                label.pack(pady=20)

                # Make popup stay on top
                popup.attributes("-topmost", True)

            InternetAwareRetryer.root_app.after(5000, lambda: InternetAwareRetryer.start(func))



