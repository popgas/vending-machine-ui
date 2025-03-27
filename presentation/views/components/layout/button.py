import tkinter as tk

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.padding import Padding


class Button(BuildableWidget):
    def __init__(self,
                 label="Button",
                 border_radius=0,
                 color="#fff",
                 pressed_color="blue",
                 padding: Padding = None,
                 ipadx=10,
                 ipady=10,
                 font_size=13,
                 letter_spacing=1,
                 icon=None,
                 on_click=None,
                 pressed_background_color="#fff",
                 background_color="blue"):
        self.label = label
        self.border_radius = border_radius
        self.color = color
        self.pressed_color = pressed_color
        self.padding = padding or Padding.zero()
        self.font_size = font_size
        self.letter_spacing = letter_spacing
        self.icon = icon
        self.on_click = on_click
        self.pressed_background_color = pressed_background_color
        self.background_color = background_color
        self.ipadx = ipadx
        self.ipady = ipady

    def build(self, parent=None):
        btn = tk.Label(parent,
                        text=self.label,
                        bg=self.background_color,
                        fg=self.color,
                        font=("Helvetica", self.font_size),
                        borderwidth=0)
        btn.pack(
            fill=tk.X,
            padx=self.padding.padx,
            pady=self.padding.pady,
            ipadx=self.ipadx,
            ipady=self.ipady,
        )

        if self.on_click is not None:
            btn.bind("<ButtonPress>", lambda x: self.on_click())

        # Set the on_click callback if provided.
        # if self.on_click:
        #     btn.configure(command=self.on_click)

        return btn
