from collections.abc import Callable

from PyQt6.QtWidgets import QVBoxLayout

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.core.state_notifier import StateNotifier
from utils.layout import LayoutUtils


class Scaffold:
    def __init__(self, parent, child: BuildableWidget | Callable[[], BuildableWidget], state:StateNotifier=None):
        self.child = child if callable(child) else lambda: child
        self.parent = parent
        self.state = state
        self.build()

        if self.state is not None:
            self.state.subscribe(lambda: self.build())

    def build(self):
        layout = self.parent.layout()

        # LayoutUtils.clear_layout(layout)
        widget = self.child().build(parent=self.parent)

        if layout is None:
            layout = QVBoxLayout(self.parent)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.parent.setLayout(layout)
            layout.addWidget(widget)
        else:
            curr_widget = layout.takeAt(0).widget()
            layout.addWidget(widget)
            layout.removeWidget(curr_widget)
            curr_widget.deleteLater()
