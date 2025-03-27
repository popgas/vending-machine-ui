from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget

from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.gpio import GpioWorker
from infrastructure.http.popgas_api import PopGasApi
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.buttons.blue_button import BlueButton
from presentation.views.components.dialogs.loading_dialog import LoadingDialog
from presentation.views.components.layout.center import CenterHorizontally
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.screens.order_completed.order_completed_state import OrderCompletedState
from application import Application
from utils.file import FileUtils


class OrderCompletedScreen(QWidget):
    def __init__(self, router: Application, order_intent: NewOrderIntent):
        super().__init__()
        router.show_bg()
        self.router = router
        self.order_intent = order_intent
        self.curr_dir = FileUtils.dir(__file__)
        self.state = OrderCompletedState()
        self.timer = self.create_timer()

        Scaffold(
            parent=self,
            state=self.state,
            child=lambda: Column(
                content_margin=30,
                children=[
                    TransparentTopBar(router, can_pop=False),
                    Column(
                        children=[
                            Row(
                                children=[
                                    ImageFromAssets(
                                        path=f"{self.curr_dir}/assets/confetti.png",
                                        width=130,
                                    ),
                                ],
                                alignment=Qt.AlignmentFlag.AlignCenter
                            ),
                            SizedBox(height=20),
                            Text("Obrigado pela compra", font_size=50, color=ColorPalette.blue3),
                            SizedBox(height=70),
                            *self.get_rating_component(),
                        ],
                        alignment=Qt.AlignmentFlag.AlignCenter,
                        flex=1
                    ),
                    CenterHorizontally(
                        width=500,
                        children=[
                            BlueButton(
                                label="Voltar ao Ínicio",
                                on_click=lambda: self.close_door_and_go_back_to_beginning(),
                            ),
                        ],
                    ),
                    SizedBox(height=70),
                ],
            ),
        )

        AudioWorker.play(f"{self.curr_dir}/assets/thanks_and_rate.mp3")

    def get_rating_component(self) -> list[BuildableWidget]:
        if not self.state.has_rated:
            return [
                CenterHorizontally(
                    width=750,
                    children=[
                        Column(
                            children=[
                                Text("Avalie a sua experiência", font_size=35, color=ColorPalette.blue3),
                                SizedBox(height=20),
                                Row(
                                    children=[
                                        self.get_rate_button("rate_1.png", "Muito Ruim", 1),
                                        self.get_rate_button("rate_2.png", "Ruim", 2),
                                        self.get_rate_button("rate_3.png", "Neutro", 3),
                                        self.get_rate_button("rate_4.png", "Boa", 4),
                                        self.get_rate_button("rate_5.png", "Muito Boa", 5),
                                    ]
                                )
                            ],
                            background_color="#fff",
                            border_radius=8,
                            content_margin=16,
                            border="1px solid #888"
                        )
                    ]
                )
            ]

        return [
            CenterHorizontally(
                width=750,
                children=[
                    Column(
                        children=[
                            Column(
                                children=[
                                    Text("Seu feedback foi enviado, muito obrigado!", font_size=35,
                                         color=ColorPalette.blue3),
                                    SizedBox(height=35),
                                    Icon("fa6s.circle-check", color=ColorPalette.green1, width=70),
                                ],
                            )
                        ],
                        background_color="#fff",
                        border_radius=8,
                        content_margin=20,
                        border="1px solid #888"
                    )
                ]
            )
        ]

    def get_rate_button(self, image, title, rating_score):
        return Column(
            children=[
                Row(
                    children=[
                        ImageFromAssets(
                            path=f"{self.curr_dir}/assets/{image}",
                            width=40,
                        ),
                    ],
                    alignment=Qt.AlignmentFlag.AlignCenter
                ),
                SizedBox(height=12),
                Text(title, font_size=15)
            ],
            on_click=lambda: self.update_rating_score(rating_score),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

    def update_rating_score(self, rating_score):
        AudioWorker.stop()

        PopGasApi.request("PUT", f"/vending-machine-orders/{self.order_intent.correlationId}/rating", json={
            'rating': rating_score,
        })

        self.state.update(has_rated=True)

        QTimer.singleShot(5000, self.close_door_and_go_back_to_beginning)

    def close_door_and_go_back_to_beginning(self):
        self.timer.stop()
        loading_dialog = LoadingDialog(message="Fechando portas...")
        loading_dialog.show()

        AudioWorker.play(f"{self.curr_dir}/assets/closing_doors.mp3")

        GpioWorker.activate(self.order_intent.get_close_door_pin())

        QTimer.singleShot(8 * 1000, lambda: loading_dialog.accept())
        QTimer.singleShot(10 * 1000, lambda: self.router.push("welcome"))

    def create_timer(self):
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self.close_door_and_go_back_to_beginning)
        timer.start(120 * 1000)

        return timer
