from PyQt6.QtCore import Qt

from presentation.config.color_palette import ColorPalette
from presentation.views.components.dialogs.info_dialog import InfoDialog
from presentation.views.components.layout.button import Button
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.text import Text
from presentation.views.components.logo import LogoWidget
from router import Router
import qtawesome as qta

class TransparentTopBar(BuildableWidget):
    def __init__(self, router: Router, can_pop=False):
        self.router = router
        self.can_pop = can_pop

    def build(self, parent=None):
        trailing = []

        if self.can_pop:
            trailing.append(
                Icon("fa6s.arrow-left",
                     color=ColorPalette.blue3,
                     size=30)
            )

        row = Row(
            children=[
                Row(
                    children=[
                        Column(children=trailing, on_click=lambda: self.pop_route())
                    ]
                ),
                Row(
                    children=[
                        LogoWidget(),
                    ],
                    alignment=Qt.AlignmentFlag.AlignCenter,
                ),
                Row(
                    children=[
                        Column(
                            children=[
                                Icon("fa6s.phone",
                                     alignment = Qt.AlignmentFlag.AlignCenter,
                                     size=23,
                                     color=ColorPalette.blue3),
                                Text("Suporte")
                            ],
                            on_click=lambda: self.on_click()
                        )
                    ],
                    alignment=Qt.AlignmentFlag.AlignRight,
                ),
            ],
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

        return row.build(parent=parent)

    def on_click(self):
        modal = InfoDialog("Suporte Técnico", "Para entrar em contato conosco:\n\nTelefone ou Whatsapp:\n0800 740 7070")
        modal.exec()  # This call is blocking and modal
        return

    def pop_route(self):
        self.router.pop()