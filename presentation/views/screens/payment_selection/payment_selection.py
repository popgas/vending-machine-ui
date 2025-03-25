import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

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
from router import Router
from utils.file import FileUtils


class PaymentSelection(QWidget):
    def __init__(self, router: Router, order_intent: NewOrderIntent):
        super().__init__()
        router.show_bg()
        self.order_intent = order_intent
        self.router = router
        self.curr_dir = FileUtils.dir(__file__)

        button_width = int(self.router.application.primaryScreen().availableSize().width() * 0.7)

        Scaffold(
            parent=self,
            child=Column(
                flex=1,
                children=[
                    TransparentTopBar(router, can_pop=True),
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
                                            size=50,
                                        ),
                                        title="Cartão de Débito",
                                        onclick=lambda: self.go_to_place_container_screen()
                                    ),
                                    SizedBox(height=30),
                                    self.payment_button(
                                        image=ImageFromAssets(
                                            path=f"{self.curr_dir}/assets/cartao.png",
                                            size=50,
                                        ),
                                        title="Cartão de Crédito",
                                        onclick=lambda: self.go_to_payment_selection_screen()
                                    ),
                                    SizedBox(height=30),
                                    self.payment_button(
                                        image=ImageFromAssets(
                                            path=f"{self.curr_dir}/assets/pix.png",
                                            size=50,
                                        ),
                                        title="PIX",
                                        onclick=lambda: self.go_to_payment_selection_screen()
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

    def go_to_place_container_screen(self):
        return

    def go_to_payment_selection_screen(self):
        return

    def payment_button(self, image, title, onclick) -> BuildableWidget:
        return Row(
            children=[
                SizedBox(width=12),
                image,
                Column(
                    children=[
                        Text(title,
                             font_size=30,
                             alignment=Qt.AlignmentFlag.AlignLeft,
                             color="#fff"),
                    ],
                ),
            ],
            background_color=ColorPalette.blue3,
            border_radius=8,
            border="1px solid #ccc",
            on_click=onclick
        )

    def get_prices(self):
        vm_id = os.environ['VENDING_MACHINE_ID']
        return PopGasApi.request("GET", f"/vending-machine-orders/{vm_id}/prices").json()
