import pathlib

import pygame
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from infrastructure.http.popgas_api import PopGasApi
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerHorizontal
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
# from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.screens.payment_selection.payment_selection import PaymentSelection
from router import Router
import os

from utils.formatter import Formatter


class ProductSelection(QWidget):
    def __init__(self, router: Router):
        super().__init__()
        router.show_bg()
        self.router = router

        prices = self.get_prices()

        Scaffold(
            parent=self,
            child=Column(
                flex=1,
                children=[
                    TransparentTopBar(router, can_pop=True),
                    Column(
                        flex=1,
                        children=[
                            Text("Selecione o produto", font_size=50, color=ColorPalette.blue3),
                        ],
                        alignment=Qt.AlignmentFlag.AlignCenter
                    ),
                    Column(
                        children=[
                            self.product_button(
                                "Recarga 13kg",
                                "eu trouxe o vasilhame vazio para troca",
                                Formatter.currency(prices['gas_refill_price']),
                                lambda: self.go_to_place_container_screen()
                            ),
                            SizedBox(height=20),
                            self.product_button(
                                "Gás 13kg + Vasilhame 13kg",
                                "não tenho vasilhame e quero comprar",
                                Formatter.currency(prices['container_price'] + prices['gas_refill_price']),
                                lambda: self.go_to_payment_selection_screen()
                            ),
                        ]
                    )
                ]
            ),
        )

        self.play_audio()

    def go_to_place_container_screen(self):
        return

    def go_to_payment_selection_screen(self):
        self.router.push(PaymentSelection(self.router))
        return

    def product_button(self, title, caption, price, onclick) -> BuildableWidget:
        return Row(
            children=[
               Column(
                   children=[
                       Text(title,
                            font_size=30,
                            alignment=Qt.AlignmentFlag.AlignLeft,
                            color=ColorPalette.blue3),
                       SizedBox(height=5),
                       Text(caption,
                            color=ColorPalette.neutralPrimary,
                            font_size=25),
                   ],
               ),
                SpacerHorizontal(),
                Text(price,
                     color=ColorPalette.blue3,
                     font_size=40),
                SizedBox(width=10),
            ],
            background_color="#fff",
            border_radius=5,
            border="1px solid #ccc",
            on_click=onclick
        )

    def play_audio(self):
        pygame.mixer.init()
        curr_dir = pathlib.Path(__file__).parent.resolve()
        pygame.mixer.music.load(f"{curr_dir}/audio.mp3")
        pygame.mixer.music.play()

    def get_prices(self):
        vm_id = os.environ['VENDING_MACHINE_ID']
        return PopGasApi.request("GET", f"/vending-machine-orders/{vm_id}/prices").json()
