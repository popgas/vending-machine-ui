import tkinter as tk
from presentation.config.color_palette import ColorPalette  # Assumes ColorPalette.textColor is defined.
from presentation.views.components.layout.padding import Padding


class Text:
    def __init__(self,
                 label="Label",
                 color=None,
                 font_family=None,
                 padding: Padding = None,
                 side=tk.TOP,
                 anchor=tk.CENTER,
                 font_size=13):
        self.label = label
        self.color = color or ColorPalette.textColor  # Use default text color.
        self.font_size = font_size
        self.font_family = font_family or "Helvetica"
        self.padding = padding or Padding.zero()
        self.side = side
        self.anchor = anchor

    def build(self, parent=None):
        label = tk.Label(parent,
                         bg=parent["bg"],
                         fg=self.color,
                         text=self.label,
                         font=("Helvetica", self.font_size))
        label.pack(
            side=self.side or parent['side'],
            anchor=self.anchor or parent['anchor'],
            pady=self.padding.pady,
            padx=self.padding.padx,
        )

        return label
