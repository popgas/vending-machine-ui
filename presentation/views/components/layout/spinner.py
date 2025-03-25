from PyQt6.QtCore import Qt, QSize
import qtawesome as qta

from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget

class Spinner(BuildableWidget):
    def __init__(self, icon=None, alignment=Qt.AlignmentFlag.AlignCenter, size=16, color=None):
        self.alignment = alignment
        self.size = size
        self.icon = icon or "mdi.loading"
        self.color = color or ColorPalette.blue2

    def build(self, parent=None):
        spin_widget = qta.IconWidget(
            color=self.color,
            size=QSize(self.size, self.size)
        )
        spin_widget.setAlignment(self.alignment)
        animation = qta.Spin(spin_widget, interval=2)
        spin_icon = qta.icon(self.icon, color=self.color, animation=animation)
        spin_widget.setIcon(spin_icon)
        return spin_widget