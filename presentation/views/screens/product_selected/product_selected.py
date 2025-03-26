import pathlib

import pygame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from domains.enums.order_product_selected import OrderProductSelected
from infrastructure.hardware.audio import AudioWorker
from infrastructure.http.popgas_api import PopGasApi
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerHorizontal
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.screens.payment_selection.payment_selection import PaymentSelection
from presentation.views.screens.place_empty_container.place_empty_container import PlaceEmptyContainer
from router import Router
import os

from utils.file import FileUtils
from utils.formatter import Formatter


class ProductSelection(QWidget):
    def __init__(self, router: Router):
        super().__init__()
        router.show_bg()
        self.router = router

        self.prices = self.get_prices()

        self.gas_refill_price = float(self.prices['gas_refill_price'])
        self.container_with_gas_price = self.gas_refill_price + float(self.prices['container_price'])

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
                                title="Recarga 13kg",
                                caption="eu trouxe o vasilhame vazio para troca",
                                price=Formatter.currency(self.gas_refill_price),
                                onclick=self.go_to_place_container_screen,
                            ),
                            SizedBox(height=20),
                            self.product_button(
                                title="Gás 13kg + Vasilhame 13kg",
                                caption="não tenho vasilhame e quero comprar",
                                price=Formatter.currency(self.container_with_gas_price),
                                onclick=self.go_to_payment_selection_screen
                            ),
                        ]
                    )
                ]
            ),
        )

        AudioWorker.delayed(f"{FileUtils.dir(__file__)}/assets/audio.mp3")

    def go_to_place_container_screen(self):
        order_intent = NewOrderIntent(
            productSelected=OrderProductSelected.gasWithContainer,
            productPrice=self.container_with_gas_price,
            stockCount=int(self.prices['container_full_stock_count']),
        )

        self.router.push(PlaceEmptyContainer(self.router, order_intent))
        return

    def go_to_payment_selection_screen(self):
        order_intent = NewOrderIntent(
            productSelected=OrderProductSelected.onlyGasRefill,
            productPrice=self.gas_refill_price,
            stockCount=int(self.prices['container_full_stock_count']),
        )

        self.router.push(PaymentSelection(self.router, order_intent))
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

    def get_prices(self):
        vm_id = os.environ['VENDING_MACHINE_ID']
        return PopGasApi.request("GET", f"/vending-machine-orders/{vm_id}/prices").json()
