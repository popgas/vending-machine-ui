from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QWidget, QSizePolicy

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.events.clickable import ClickableWidget
import uuid

class Row(BuildableWidget):
    def __init__(self,
                 children: list[BuildableWidget] = None,
                 padding="0",
                 border_radius=0,
                 border="transparent",
                 flex=None,
                 on_click=None,
                 width=None,
                 height=None,
                 background_color="transparent",
                 alignment=Qt.AlignmentFlag.AlignLeft):
        self.children = children or []
        self.alignment = alignment
        self.on_click = on_click
        self.padding = padding
        self.border = border
        self.border_radius = border_radius
        self.background_color = background_color
        self.flex=flex
        self.width = width
        self.height = height
        self.name=str(uuid.uuid4().hex)

    def build(self, parent=None):
        widget = QWidget(parent)

        if self.on_click:
            widget = ClickableWidget(parent=parent)
            widget.clicked.connect(self.on_click)

        if self.width is not None:
            widget.setFixedWidth(self.width)
        if self.height is not None:
            widget.setFixedHeight(self.height)

        layout = QHBoxLayout()
        layout.setAlignment(self.alignment)

        widget.setLayout(layout)
        widget.setObjectName(self.name)
        widget.setStyleSheet(f"""
            #{self.name} {{
                border-radius: {self.border_radius}px;
                border: {self.border};
                background-color: {self.background_color};
                padding: {self.padding};
            }}
        """)

        widget.setSizePolicy(QSizePolicy.Policy.Expanding, widget.sizePolicy().verticalPolicy())

        if self.flex:
            widget.flex = self.flex

        for child in self.children:
            layout.addWidget(child.build(parent=widget))

        return widget