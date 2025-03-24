from PyQt6.QtWidgets import QVBoxLayout

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget


class Scaffold:
    def __init__(self, parent, child: BuildableWidget):
        self.child = child
        self.parent = parent

        self.build()

    def build(self):
        layout = QVBoxLayout(self.parent)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.parent.setLayout(layout)

        layout.addWidget(self.child.build(parent=self.parent))
