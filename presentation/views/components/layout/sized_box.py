import tkinter as tk
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.enums.alignment import Side


class SizedBox(BuildableWidget):
    def __init__(self, width: int = 0, height: int = 0):
        self.width = width
        self.height = height

    def build(self, parent=None):
        widget = tk.Frame(parent, bg=parent["bg"], width=self.width, height=self.height)
        widget.pack(
            fill="both",
            side=Side.LEFT if self.width > 0 else Side.TOP,
        )

        return widget