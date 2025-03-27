import tkinter as tk
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.button import Button
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.padding import Padding
from presentation.views.components.layout.spacer import SpacerVertical
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from router import Router

class WelcomeScreen(tk.Frame):
    def __init__(self, router: Router):
        super().__init__(router.container, bg="#ECEFF1")
        self.router = router

        Scaffold(
            parent=self,
            child=Column(
                expand=True,
                anchor=tk.CENTER,
                children=[
                    TransparentTopBar(router),
                    Column(
                        expand=True,
                        children=[
                            SpacerVertical(),
                            Text("Bem-vindo", font_size=40, color=ColorPalette.blue3),
                            Text("Máquina de Auto Atendimento",
                                 font_size=40,
                                 padding=Padding.vertical(15),
                                 color=ColorPalette.blue3),
                            Text("24h", font_size=60, color=ColorPalette.blue3),
                            SpacerVertical(),
                        ],
                        anchor=tk.CENTER,
                    ),
                    Button(
                        label="Toque para Iniciar",
                        on_click=lambda: router.push('product_selection'),
                        background_color=ColorPalette.blue3,
                        pressed_background_color=ColorPalette.blue2,
                        pressed_color="#fff",
                        font_size=30,
                        ipadx=20,
                        ipady=20,
                        padding=Padding.all(20),
                    ),
                ],
            )
        )
