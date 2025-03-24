from PyQt6.QtWidgets import QWidget

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget


class SizedBox(BuildableWidget):
    def __init__(self, width: int = None, height: int = None):
        self.width = width
        self.height = height

    def build(self, parent=None):
        widget = QWidget(parent)
        if self.width is not None:
            widget.setFixedWidth(self.width)
        if self.height is not None:
            widget.setFixedHeight(self.height)
        return widget