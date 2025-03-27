import tkinter as tk
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.padding import Padding
from PIL import Image, ImageTk

class ImageFromAssets(BuildableWidget):
    def __init__(self, path, width=80, height=80, anchor=tk.W, padding: Padding = None):
        self.path = path
        self.width = width
        self.height = height
        self.anchor = anchor
        self.img = None
        self.padding = padding or Padding.zero()

    def build(self, parent=None):
        original_image = Image.open(self.path)
        resized_image = original_image.resize((self.width, self.height))  # Width, Height

        tk_image = ImageTk.PhotoImage(resized_image)

        label = tk.Label(parent,
                         width=self.width,
                         height=self.height,
                         image=tk_image,
                         bg=parent['bg'])
        label.image = tk_image
        label.pack(
            anchor=self.anchor,
            expand=False,
            fill=tk.NONE,
            padx=self.padding.padx,
            pady=self.padding.pady,
        )

        return label