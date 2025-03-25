from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from presentation.config.color_palette import ColorPalette
from presentation.views.components.buttons.blue_button import BlueButton
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.screens.product_selected.product_selected import ProductSelection
from router import Router


class WelcomeScreen(QWidget):
    def __init__(self, router: Router):
        super().__init__()
        router.show_bg()
        self.router = router

        Scaffold(
            parent=self,
            child=Column(
                flex=1,
                children=[
                    TransparentTopBar(router),
                    Column(
                        flex=1,
                        children=[
                            Text("Bem-vindo", font_size=40, color=ColorPalette.blue3),
                            Text("Máquina de Auto Atendimento", font_size=40, padding="15px 0",
                                 color=ColorPalette.blue3),
                            Text("24h", font_size=60, color=ColorPalette.blue3),
                        ],
                        alignment=Qt.AlignmentFlag.AlignCenter
                    ),
                    BlueButton(
                        label="Toque para Iniciar",
                        on_click=lambda: router.push(ProductSelection(router))
                    ),
                ]
            )
        )
