import tkinter as tk
import uuid

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.padding import Padding


class RowAlignment:
    center="w"

class Row(BuildableWidget):
    def __init__(self,
                 children: list = None,
                 padding: Padding = None,
                 content_margin=0,
                 border_radius=0,   # Not directly supported in Tkinter.
                 border="transparent",  # We'll simulate a border if needed.
                 flex=None,
                 on_click=None,
                 width=None,
                 height=None,
                 expand=True,
                 background_color=None,
                 side=tk.LEFT,
                 anchor=tk.N):  # Using Tkinter anchor strings: "w", "center", "e", etc.
        self.children = children or []
        self.on_click = on_click
        self.padding = padding or Padding.zero()
        self.border = border
        self.expand = expand
        self.border_radius = border_radius
        self.background_color = background_color
        self.flex = flex
        self.width = width
        self.height = height
        self.side = side
        self.anchor = anchor
        self.name = str(uuid.uuid4().hex)

        if isinstance(content_margin, int):
            # Convert a single int into a tuple: (left, top, right, bottom)
            self.content_margin = (content_margin, content_margin, content_margin, content_margin)
        else:
            self.content_margin = content_margin

    def build(self, parent=None):
        bg =self.background_color or parent["bg"]
        widget = tk.Frame(parent, bg=bg)
        widget.pack(
            fill="x",
            expand=self.expand,
            side=self.side,
            anchor=self.anchor,
            padx=self.padding.padx,
            pady=self.padding.pady,
        )

        for child in self.children:
            child.build(widget)

        # If expanded or flex is specified, the parent should handle layout with expand=True.
        # Here we simply return the widget.
        return widget
