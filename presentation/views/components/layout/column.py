import uuid

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
                 width=None,
                 height=None,
                 padding="0",
                 content_margin=0,
                 border_radius=0,
                 border="transparent",
                 alignment=Qt.AlignmentFlag.AlignTop):
        self.children = children or []
        self.spacing = spacing
        self.flex = flex
        self.on_click = on_click
        self.alignment = alignment
        self.expanded = expanded
        self.width = width
        self.height = height
        self.padding = padding
        self.border = border
        self.border_radius = border_radius
        self.background_color = background_color
        self.name = str(uuid.uuid4().hex)

        if isinstance(content_margin, int):
            content_margin=(content_margin, content_margin, content_margin, content_margin)

        self.content_margin = content_margin

    def build(self, parent=None):
        widget = QWidget(parent)

        if self.on_click:
            widget = ClickableWidget(parent)
            widget.clicked.connect(self.on_click)

        if self.width is not None:
            widget.setFixedWidth(self.width)
        if self.height is not None:
            widget.setFixedHeight(self.height)

        layout = QVBoxLayout()
        layout.setSpacing(self.spacing)
        layout.setAlignment(self.alignment)
        widget.setLayout(layout)
        layout.setContentsMargins(*self.content_margin)

        if self.flex:
            widget.flex = self.flex
            widget.setSizePolicy(widget.sizePolicy().horizontalPolicy(), QSizePolicy.Policy.Expanding)
        elif self.expanded:
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)

        widget.setObjectName(self.name)
        widget.setStyleSheet(f"""
            #{self.name} {{
                border-radius: {self.border_radius}px;
                border: {self.border};
                background-color: {self.background_color};
                padding: {self.padding};
            }}
        """)

        for child in self.children:
            layout.addWidget(child.build(parent=widget))

        return widget