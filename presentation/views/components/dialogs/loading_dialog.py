from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout

from presentation.views.components.layout.column import Column
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spinner import Spinner
from presentation.views.components.layout.text import Text


class LoadingDialog(QDialog):
    def __init__(self, message, parent=None, alignment=Qt.AlignmentFlag.AlignLeft):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setModal(True)

        # Apply a custom style sheet (optional)
        self.setStyleSheet("""
            QDialog {
                background-color: #fff;
                border: 1px solid #bbb;
                border-radius: 10px;
            }
        """)

        # Create layout and widgets
        layout = QVBoxLayout(self)
        layout.addWidget(
            Column(
                children=[
                    Text(message, alignment=alignment, font_size=20),
                    SizedBox(height=24),
                    Spinner(size=120)
                ]
            ).build(parent=self)
        )