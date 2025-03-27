# from PyQt6.QtCore import Qt

from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.row import Row


class CenterHorizontally(BuildableWidget):
    def __init__(self, children: list[BuildableWidget], width=None):
        self.width = width
        self.children = children

    def build(self, parent=None):
        return Row(
            children=[
                Column(
                    width=self.width,
                    children=self.children),
            ],
            alignment=Qt.AlignmentFlag.AlignCenter,
        ).build(parent=parent)


class CenterVertically(BuildableWidget):
    def __init__(self, children: list[BuildableWidget]):
        self.children = children

    def build(self, parent=None):
        return Row(
            children=[
                Column(
                    width=self.width,
                    children=self.children),
            ],
            alignment=Qt.AlignmentFlag.AlignCenter,
        ).build(parent=parent)