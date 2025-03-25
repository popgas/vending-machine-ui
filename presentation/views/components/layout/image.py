from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget

class ImageFromAssets(BuildableWidget):
    def __init__(self, path, size=80):
        self.path = path
        self.size = size

    def build(self, parent=None):
        label = QLabel(parent)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedWidth(self.size)
        pixmap = QPixmap(self.path)
        scaled_pixmap = pixmap.scaledToWidth(self.size, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label