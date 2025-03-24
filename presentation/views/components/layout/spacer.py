from PyQt6.QtWidgets import QWidget, QSizePolicy

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget

class SpacerVertical(BuildableWidget):
    def build(self, parent=None):
        widget = QWidget()
        widget.flex = 1
        widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        return widget

class SpacerHorizontal(BuildableWidget):
    def build(self, parent=None):
        widget = QWidget()
        widget.flex = 1
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        return widget

class Spacer(BuildableWidget):
    def build(self, parent=None):
        widget = QWidget()
        widget.flex = 1
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return widget