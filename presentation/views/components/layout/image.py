import tkinter as tk
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.padding import Padding


class ImageFromAssets(BuildableWidget):
    def __init__(self, path, size=None, anchor=tk.W, padding: Padding = None):
        self.path = path
        self.size = size
        self.anchor = anchor
        self.img = None
        self.padding = padding or Padding.zero()

    def build(self, parent=None):
        photo = tk.PhotoImage(file=self.path)

        label = tk.Label(parent, image=photo, bg=parent['bg'])
        label.image = photo
        label.pack(
            anchor=self.anchor,
            expand=False,
            fill=tk.NONE,
            padx=self.padding.padx,
            pady=self.padding.pady,
        )

        return label