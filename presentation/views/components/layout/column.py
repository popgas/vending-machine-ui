import uuid

import tkinter as tk

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.enums.alignment import Side, Anchor, Fill
from presentation.views.components.layout.padding import Padding


class Column(BuildableWidget):
    def __init__(self,
                 children: list = [],
                 background_color=None,
                 spacing=0,
                 on_click=None,
                 expand=False,
                 width=0,
                 height=0,
                 padding: Padding = None,
                 border_radius=0,
                 side=Side.TOP,
                 anchor=Anchor.TOP,
                 border_color=None,
                 fill=Fill.BOTH,
                 border_width=1):  # "n" for top alignment in Tkinter.
        self.children = children or []
        self.spacing = spacing
        self.on_click = on_click
        self.expand = expand
        self.width = width
        self.height = height
        self.padding = padding or Padding.zero()
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius  # Not supported in Tkinter.
        self.background_color = background_color
        self.side = side
        self.anchor = anchor
        self.fill = fill
        self.name = uuid.uuid4().hex

    def build(self, parent=None):
        bg = self.background_color or parent["bg"]
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

        if self.width > 0 or self.height > 0:
            widget.pack_propagate(0)

        if self.border_color is not None:
            widget.config(highlightbackground=self.border_color, highlightthickness=self.border_width)

        for child in self.children:
            child.build(parent=widget)

        if self.on_click is not None:
            widget.bind("<ButtonPress>", lambda x: self.on_click())

            for child in widget.winfo_children():
                child.bind("<ButtonPress>", lambda x: self.on_click())

        return widget