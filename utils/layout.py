from PyQt6.QtCore import QObjectCleanupHandler
from PyQt6.QtWidgets import QWidget


class LayoutUtils:
    @staticmethod
    def clear_layout(layout):
        if layout is not None:
            # QWidget().setLayout(layout)
            QObjectCleanupHandler().add(layout)