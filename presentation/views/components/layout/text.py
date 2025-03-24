from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel

from presentation.config.color_palette import ColorPalette
from presentation.config.font import GeistFont
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget

class Text(BuildableWidget):
    def __init__(self,
                 label="Label",
                 alignment=Qt.AlignmentFlag.AlignCenter,
                 color=None,
                 font_family=None,
                 padding="0px",
                 font_size=13):
        self.label = label
        self.color = color or ColorPalette.textColor
        self.alignment = alignment
        self.font_size = font_size
        self.font_family = font_family or GeistFont.light()
        self.padding = padding

    def build(self, parent=None):
        label = QLabel(self.label)
        label.setAlignment(self.alignment)
        label.setStyleSheet(f"""
            color: {self.color};
            padding: {self.padding};
            font-weight: normal;
        """)

        font = QFont(self.font_family, self.font_size)
        label.setFont(font)

        label.setFont(font)
        return label