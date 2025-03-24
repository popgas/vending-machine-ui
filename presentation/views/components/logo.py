from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget

class LogoWidget(BuildableWidget):
    def build(self, parent=None):
        label = QLabel(parent)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedWidth(80)
        pixmap = QPixmap("./images/colored-logo.svg")
        scaled_pixmap = pixmap.scaledToWidth(80, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        return label