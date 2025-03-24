from PyQt6.QtCore import Qt, QSize
import qtawesome as qta
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget

class Icon(BuildableWidget):
    def __init__(self, icon=None, alignment=Qt.AlignmentFlag.AlignCenter, size=16, color="blue"):
        self.alignment = alignment
        self.size = size
        self.icon = icon
        self.color = color

    def build(self, parent=None):
        label = qta.IconWidget(self.icon, color=self.color,size=QSize(self.size, self.size))
        label.setAlignment(self.alignment)
        return label