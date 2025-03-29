import os

import tkinter as tk
from domains.enums.order_product_selected import OrderProductSelected
from infrastructure.hardware.audio import AudioWorker
from infrastructure.http.popgas_api import PopGasApi
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.enums.alignment import Side, Anchor
from presentation.views.components.layout.padding import Padding
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerHorizontal, SpacerVertical
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.state_provider import StateProvider
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from application import Application
from utils.file import FileUtils
from utils.formatter import Formatter


class ProductSelectionScreen(tk.Frame):
    def __init__(self, app: Application):
        super().__init__(app.container, bg="#ECEFF1")
        self.app = app

        self.data = self.get_data()

        if int(self.data['container_full_stock_count']) == 0:
            app.off_all('empty_stock')
            return

        if 'is_under_maintenance' in self.data and bool(self.data['is_under_maintenance']):
            app.off_all('tech_support')
            return

        self.gas_refill_price = float(self.data['gas_refill_price'])
        self.container_with_gas_price = self.gas_refill_price + float(self.data['container_price'])

        StateProvider(
            parent=self,
            child=Column(
                expand=True,
                children=[
                    TransparentTopBar(app, can_pop=True),
                    Column(
                        expand=True,
                        children=[
                            SpacerVertical(),
                            Text("Selecione o produto", font_size=40, color=ColorPalette.blue3),
                            SpacerVertical(),
                            self.product_button(
                                title="Recarga 13kg",
                                caption="eu trouxe o vasilhame vazio para troca",
                                price=Formatter.currency(self.gas_refill_price),
                                onclick=self.go_to_place_container_screen,
                            ),
                            self.product_button(
                                title="Gás 13kg + Vasilhame 13kg",
                                caption="não tenho vasilhame e quero comprar",
                                price=Formatter.currency(self.container_with_gas_price),
                                onclick=self.go_to_payment_selection_screen
                            ),
                        ],
                    ),
                ]
            ),
        )


        AudioWorker.play(f"{FileUtils.dir(__file__)}/assets/audio.mp3")

    def go_to_place_container_screen(self):
        order_intent = NewOrderIntent(
            productSelected=OrderProductSelected.onlyGasRefill,
            productPrice=self.container_with_gas_price,
            stockCount=int(self.data['container_full_stock_count']),
        )

        self.app.push('place_empty_container', order_intent)
        return

    def go_to_payment_selection_screen(self):
        order_intent = NewOrderIntent(
            productSelected=OrderProductSelected.gasWithContainer,
            productPrice=self.gas_refill_price,
            stockCount=int(self.data['container_full_stock_count']),
        )

        self.app.push('payment_selection', order_intent)
        return

    def product_button(self, title, caption, price, onclick) -> BuildableWidget:
        return Column(
            border_radius=5,
            border_color="#ccc",
            background_color=ColorPalette.blue3,
            on_click=onclick,
            padding=Padding(left=20, right=20, bottom=20),
            children=[
                Row(
                    padding=Padding.all(20),
                    children=[
                        Column(
                            children=[
                                Text(title,
                                     font_size=22,
                                     anchor=Anchor.LEFT,
                                     color="#fff"),
                                SizedBox(height=5),
                                Text(caption,
                                    anchor=Anchor.LEFT,
                                     color="#fff",
                                     font_size=15),
                            ],
                            side=Side.LEFT,
                            on_click=onclick,
                        ),
                        SpacerHorizontal(),
                        Text(price,
                             color="#99E6FD",
                             anchor=Anchor.TOP_RIGHT,
                             padding=Padding(bottom=15),
                             font_size=30),
                    ],
                    on_click=onclick,
                )
            ]
        )

    def get_data(self):
        vm_id = os.environ['VENDING_MACHINE_ID']
        return PopGasApi.request("GET", f"/vending-machine-orders/{vm_id}/prices").json()
