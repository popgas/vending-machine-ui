from PyQt6.QtWidgets import QPushButton
import qtawesome as qta
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget

class FontAwesome6RegularIcon(BuildableWidget):
    def __init__(self, name="flag"):
        self.name = name

    def build(self, parent=None):
        fa6_icon = qta.icon(f'fa6.{self.name}')
        fa6_button = QPushButton(fa6_icon, 'Font Awesome 6! (regular)')
        return fa6_button