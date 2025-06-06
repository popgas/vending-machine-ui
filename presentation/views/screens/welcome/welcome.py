import tkinter as tk
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.button import Button
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.enums.alignment import Anchor
from presentation.views.components.layout.padding import Padding
from presentation.views.components.layout.spacer import SpacerVertical
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.state_provider import StateProvider
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from application import Application

class WelcomeScreen(tk.Frame):
    def __init__(self, app: Application):
        super().__init__(app.container, bg="#FFF")
        self.app = app

        StateProvider(
            parent=self,
            child=Column(
                expand=True,
                anchor=Anchor.CENTER,
                children=[
                    TransparentTopBar(app),
                    Column(
                        expand=True,
                        children=[
                            SpacerVertical(),
                            Text("Bem-vindo", font_size=40, color=ColorPalette.blue3),
                            Text("Máquina de Auto Atendimento",
                                 font_size=30,
                                 padding=Padding.vertical(15),
                                 color=ColorPalette.blue3),
                            Text("24h", font_size=60, color=ColorPalette.blue3),
                            SpacerVertical(),
                        ],
                        anchor=Anchor.CENTER,
                    ),
                    Button(
                        label="Toque para Iniciar",
                        on_click=lambda: self.go_to_product_selection(),
                        background_color=ColorPalette.blue3,
                        pressed_background_color=ColorPalette.blue2,
                        pressed_color="#fff",
                        font_size=30,
                        ipadx=20,
                        ipady=50,
                        padding=Padding.all(20),
                    ),
                ],
            )
        )

    def go_to_product_selection(self):
        self.app.push('product_selection')