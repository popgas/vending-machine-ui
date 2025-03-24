from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

class InfoDialog(QDialog):
    def __init__(self, title, message, parent=None, alignment=Qt.AlignmentFlag.AlignLeft):
        super().__init__(parent)
        self.setWindowTitle(title)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setModal(True)

        # Apply a custom style sheet (optional)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                border: 1px solid #bbb;
                border-radius: 5px;
            }
            QLabel {
                color: #333333;
                font-size: 17pt;
                font-weight: normal;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                width: 100%;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #005F99;
            }
        """)

        # Create layout and widgets
        layout = QVBoxLayout(self)
        message_label = QLabel(message)
        message_label.setAlignment(alignment)
        layout.addWidget(message_label)

        # Buttons layout
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)  # Closes the dialog with accept

        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.resize(300, 150)