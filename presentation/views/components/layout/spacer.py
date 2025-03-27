from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
import tkinter as tk

class SpacerVertical(BuildableWidget):
    def build(self, parent=None):
        widget = tk.Frame(parent, bg=parent['bg'])
        widget.pack(
            fill="y",
            expand=True,
        )

class SpacerHorizontal(BuildableWidget):
    def build(self, parent=None):
        widget = tk.Frame(parent, bg=parent['bg'])
        widget.pack(
            fill="x",
            expand=True,
        )
#
# class Spacer(BuildableWidget):
#     def build(self, parent=None):
#         widget = QWidget()
#         widget.flex = 1
#         widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
#         return widget