import tkinter as tk
import uuid

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.enums.alignment import Side, Anchor, Fill
from presentation.views.components.layout.padding import Padding


class Row(BuildableWidget):
    def __init__(self,
                 children: list = None,
                 padding: Padding = None,
                 border_radius=0,
                 flex=None,
                 on_click=None,
                 width=None,
                 height=None,
                 expand=True,
                 background_color=None,
                 border_color=None,
                 border_width=1,
                 side=Side.LEFT,
                 fill=Fill.X,
                 anchor=Anchor.TOP):
        self.children = children or []
        self.on_click = on_click
        self.padding = padding or Padding.zero()
        self.expand = expand
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.background_color = background_color
        self.flex = flex
        self.width = width
        self.height = height
        self.side = side
        self.anchor = anchor
        self.fill = fill
        self.name = str(uuid.uuid4().hex)

    def build(self, parent=None):
        bg =self.background_color or parent["bg"]
        widget = tk.Frame(parent,
                          width=self.width,
                          height=self.height,
                          bg=bg)
        widget.pack(
            fill=self.fill,
            expand=self.expand,
            side=self.side,
            anchor=self.anchor,
            padx=self.padding.padx,
            pady=self.padding.pady,
        )

        if self.border_color is not None:
            widget.config(highlightbackground=self.border_color, highlightthickness=self.border_width)

        for child in self.children:
            child.build(widget)

        if self.on_click is not None:
            widget.bind("<ButtonPress>", lambda x: self.on_click())

            for child in widget.winfo_children():
                child.bind("<ButtonPress>", lambda x: self.on_click())

        return widget
