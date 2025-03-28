import tkinter as tk

from domains.enums.order_product_selected import OrderProductSelected
from infrastructure.hardware.audio import AudioWorker
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.enums.alignment import Side, Anchor, Fill
from presentation.views.components.layout.image import ImageFromAssets
from presentation.views.components.layout.padding import Padding
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerVertical
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from application import Application
from utils.file import FileUtils


class PaymentSelectionScreen(tk.Frame):
    def __init__(self, app: Application, order_intent: NewOrderIntent):
        super().__init__(app.container, bg="#ECEFF1")
        self.order_intent = order_intent
        self.app = app
        self.curr_dir = FileUtils.dir(__file__)

        can_pop = order_intent.productSelected == OrderProductSelected.gasWithContainer

        Scaffold(
            parent=self,
            child=Column(
                expand=True,
                padding=Padding.all(30),
                children=[
                    TransparentTopBar(app, can_pop=can_pop),
                    Column(
                        expand=True,
                        children=[
                            SpacerVertical(),
                            Text("Selecione a forma de pagamento", font_size=40, color=ColorPalette.blue3),
                            SizedBox(height=100),
                            Column(
                                expand=True,
                                children=[
                                    self.payment_button(
                                        image=ImageFromAssets(
                                            path=f"{self.curr_dir}/assets/cartao.png",
                                            width=58,
                                            height=57,
                                        ),
                                        title="Cartão de Débito",
                                        onclick=lambda: self.debit_card()
                                    ),
                                    SizedBox(height=10),
                                    self.payment_button(
                                        image=ImageFromAssets(
                                            path=f"{self.curr_dir}/assets/cartao.png",
                                            width=58,
                                            height=57,
                                        ),
                                        title="Cartão de Crédito",
                                        onclick=lambda: self.credit_card()
                                    ),
                                    SizedBox(height=10),
                                    self.payment_button(
                                        image=ImageFromAssets(
                                            path=f"{self.curr_dir}/assets/pix.png",
                                            width=58,
                                            height=57,
                                        ),
                                        title="PIX",
                                        onclick=lambda: self.pix_machine()
                                    ),
                                ],
                            ),
                            SpacerVertical(),
                        ],
                    ),
                ]
            )
        )

        AudioWorker.play(f"{self.curr_dir}/assets/audio.mp3")

    def payment_button(self, image, title, onclick) -> BuildableWidget:
        return Row(
            expand=True,
            side=Side.TOP,
            fill=Fill.NONE,
            children=[
                Row(
                    width=600,
                    height=100,
                    children=[
                        SizedBox(width=30),
                        image,
                        SizedBox(width=20),
                        Text(title,
                             font_size=24,
                             side=Side.LEFT,
                             anchor=Anchor.RIGHT,
                             color="#fff"),
                    ],
                    background_color=ColorPalette.blue3,
                    border_radius=8,
                    fill=Fill.X,
                    border_color="#ccc",
                    on_click=onclick,
                )
            ]
        )

    def debit_card(self):
        AudioWorker.stop()
        self.app.push('card_machine', self.order_intent.copy_with(
            paymentMethodId=2
        ))

    def credit_card(self):
        AudioWorker.stop()
        self.app.push('card_machine', self.order_intent.copy_with(
            paymentMethodId=3
        ))

    def pix_machine(self):
        AudioWorker.stop()
        self.app.push('card_machine', self.order_intent.copy_with(
            paymentMethodId=5
        ))
