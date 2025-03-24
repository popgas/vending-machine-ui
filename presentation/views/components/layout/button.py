from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget

class Button(BuildableWidget):
    def __init__(self,
                 label="Button",
                 border_radius=0,
                 color="#fff",
                 pressed_color="blue",
                 padding="10px 0",
                 font_size=13,
                 letter_spacing=1,
                 icon=None,
                 on_click=None,
                 pressed_background_color="#fff",
                 background_color="blue"):
        self.icon = icon
        self.label = label
        self.padding = padding
        self.font_size = font_size
        self.border_radius = border_radius
        self.letter_spacing = letter_spacing
        self.color = color
        self.on_click = on_click
        self.background_color = background_color
        self.pressed_color = pressed_color
        self.pressed_background_color = pressed_background_color

    def build(self, parent=None):
        button = QPushButton(self.label)

        if self.icon:
            button=QPushButton(self.icon, self.label)

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.background_color};
                border-radius: {self.border_radius}px;
                font-size: {self.font_size}pt;
                color: {self.color};
                padding: {self.padding};
                letter-spacing: {self.letter_spacing}px;
            }}
            QPushButton:hover {{
                background-color: {self.pressed_background_color};
                color: {self.pressed_color};
            }}
            QPushButton:pressed {{
                background-color: {self.pressed_background_color};
                color: {self.pressed_color};
            }}
        """)

        if self.on_click:
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(self.on_click)

        return button