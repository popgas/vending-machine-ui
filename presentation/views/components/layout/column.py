from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.events.clickable import ClickableWidget


class Column(BuildableWidget):
    def __init__(self,
                 children: list[BuildableWidget],
                 background_color=None,
                 spacing=0,
                 on_click=None,
                 expanded=False,
                 flex=None,
                 alignment=Qt.AlignmentFlag.AlignTop):
        self.children = children or []
        self.spacing = spacing
        self.flex = flex
        self.on_click = on_click
        self.alignment = alignment
        self.expanded = expanded
        self.background_color = background_color

    def build(self, parent=None):
        widget = QWidget(parent)

        if self.on_click:
            widget = ClickableWidget(parent)
            widget.clicked.connect(self.on_click)

        layout = QVBoxLayout()
        layout.setSpacing(self.spacing)
        layout.setAlignment(self.alignment)
        widget.setLayout(layout)

        if self.flex:
            widget.flex = self.flex
            widget.setSizePolicy(widget.sizePolicy().horizontalPolicy(), QSizePolicy.Policy.Expanding)
        elif self.expanded:
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)

        if self.background_color:
            widget.setStyleSheet(f"background-color: {self.background_color};")

        for child in self.children:
            layout.addWidget(child.build(parent=widget))

        return widget