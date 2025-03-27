import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from domains.enums.order_product_selected import OrderProductSelected
from infrastructure.hardware.audio import AudioWorker
from infrastructure.http.popgas_api import PopGasApi
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.image import ImageFromAssets
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from application import Application
from utils.file import FileUtils


class PaymentSelectionScreen(QWidget):
    def __init__(self, router: Application, order_intent: NewOrderIntent):
        super().__init__()
        router.show_bg()
        self.order_intent = order_intent
        self.router = router
        self.curr_dir = FileUtils.dir(__file__)

        button_width = int(self.router.application.primaryScreen().availableSize().width() * 0.7)
        can_pop = order_intent.productSelected == OrderProductSelected.gasWithContainer
        print(order_intent.productSelected)
        print(OrderProductSelected.gasWithContainer)
        print(can_pop)

        Scaffold(
            parent=self,
            child=Column(
                flex=1,
                content_margin=30,
                children=[
                    TransparentTopBar(router, can_pop=can_pop),
                    Column(
                        flex=1,
                        children=[
                            Text("Selecione a forma de pagamento", font_size=50, color=ColorPalette.blue3),
                            SizedBox(height=100),
                            Column(
                                width=button_width,
                                children=[
                                    self.payment_button(
                                        image=ImageFromAssets(
                                            path=f"{self.curr_dir}/assets/cartao.png",
                                            width=50,
                                        ),
                                        title="Cartão de Débito",
                                        onclick=lambda: self.debit_card()
                                    ),
                                    SizedBox(height=30),
                                    self.payment_button(
                                        image=ImageFromAssets(
                                            path=f"{self.curr_dir}/assets/cartao.png",
                                            width=50,
                                        ),
                                        title="Cartão de Crédito",
                                        onclick=lambda: self.credit_card()
                                    ),
                                    SizedBox(height=30),
                                    self.payment_button(
                                        image=ImageFromAssets(
                                            path=f"{self.curr_dir}/assets/pix.png",
                                            width=50,
                                        ),
                                        title="PIX",
                                        onclick=lambda: self.pix_machine()
                                    ),
                                ]
                            )
                        ],
                        alignment=Qt.AlignmentFlag.AlignCenter
                    ),
                ]
            )
        )

        AudioWorker.play(f"{self.curr_dir}/assets/audio.mp3")

    def payment_button(self, image, title, onclick) -> BuildableWidget:
        return Row(
            content_margin=20,
            children=[
                image,
                SizedBox(width=10),
                Column(
                    content_margin=(0, 5, 0, 0),
                    children=[
                        Text(title,
                             font_size=30,
                             alignment=Qt.AlignmentFlag.AlignLeft,
                             color="#fff"),
                    ]
                )
            ],
            background_color=ColorPalette.blue3,
            border_radius=8,
            border="1px solid #ccc",
            on_click=onclick,
            alignment=Qt.AlignmentFlag.AlignVCenter,
        )

    def debit_card(self):
        AudioWorker.stop()
        self.router.push('card_machine', self.order_intent.copy_with(
            paymentMethodId=2
        ))

    def credit_card(self):
        AudioWorker.stop()
        self.router.push('card_machine', self.order_intent.copy_with(
            paymentMethodId=3
        ))

    def pix_machine(self):
        AudioWorker.stop()
        self.router.push('card_machine', self.order_intent.copy_with(
            paymentMethodId=5
        ))
