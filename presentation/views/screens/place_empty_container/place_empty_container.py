from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget

from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.gpio import GpioWorker
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerHorizontal
from presentation.views.components.layout.spinner import Spinner
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.screens.place_empty_container.place_empty_container_state import PlaceEmptyContainerState
from router import Router
from utils.file import FileUtils


class PlaceEmptyContainerScreen(QWidget):
    def __init__(self, router: Router, order_intent: NewOrderIntent):
        super().__init__()
        router.hide_bg()
        self.router = router
        self.order_intent = order_intent
        self.curr_dir = FileUtils.dir(__file__)
        self.state = PlaceEmptyContainerState()
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.handle_timer)
        self.timer.start()

        Scaffold(
            parent=self,
            state=self.state,
            child=lambda: Column(
                content_margin=30,
                children=[
                    TransparentTopBar(router, can_pop=False),
                    Column(
                        flex=1,
                        children=[
                            Text("Insira seu botijão vazio", font_size=50, color=ColorPalette.blue3),
                            SizedBox(height=20),
                            Text("Coloque seu botijão vazio na porta que se abriu e afaste-se", font_size=30,
                                 alignment=Qt.AlignmentFlag.AlignCenter),
                            *self.get_timer_text(),
                            SizedBox(height=40),
                            Row(
                                children=[
                                    Column(
                                        content_margin=30,
                                        background_color="#ffffff",
                                        border_radius=10,
                                        border="1px solid #ccc",
                                        children=[
                                            ImageFromAssets(
                                                path=f"{self.curr_dir}/assets/instrucoes_colocar_botijao.png",
                                                size=300,
                                            ),
                                        ]
                                    )
                                ],
                                alignment=Qt.AlignmentFlag.AlignCenter,
                            ),
                            SizedBox(height=40),
                            self.get_button_or_closing_door_spinner(),
                        ],
                        alignment=Qt.AlignmentFlag.AlignCenter
                    ),
                ]
            ),
        )

        AudioWorker.delayed(f"{self.curr_dir}/assets/audio.mp3")
        QTimer.singleShot(150, lambda: GpioWorker.activate(self.order_intent.get_open_door_pin()))

    def go_to_camera_verification_part1(self):
        self.state.update(closing_door=True, timer_reached_zero=True)
        self.timer.stop()
        QTimer.singleShot(150, self.go_to_camera_verification_part2)

    def go_to_camera_verification_part2(self):
        AudioWorker.delayed(f"{self.curr_dir}/assets/door_will_close.mp3")
        QTimer.singleShot(5 * 1000, lambda: GpioWorker.activate(self.order_intent.get_close_door_pin()))
        QTimer.singleShot(10 * 1000, self.go_to_camera_verification_part3)

    def go_to_camera_verification_part3(self):
        self.state.update(closing_door=False)
        self.router.push('camera_verification', self.order_intent)

    def get_button_or_closing_door_spinner(self):
        if self.state.closing_door:
            return Column(
                children=[
                    Spinner(size=70),
                    Text("Fechando porta, afaste-se por favor!",
                         font_size=30,
                         alignment=Qt.AlignmentFlag.AlignCenter,
                         color="#333"),
                ]
            )

        return Row(
            children=[
                Row(
                    children=[
                        SizedBox(width=10),
                        Text("Pronto. Já coloquei meu botijão",
                             font_size=30,
                             alignment=Qt.AlignmentFlag.AlignLeft,
                             color="#fff"),
                        SpacerHorizontal(),
                        Icon("fa6s.arrow-right",
                             alignment=Qt.AlignmentFlag.AlignCenter,
                             size=40,
                             color="#fff"),
                        SizedBox(width=10),
                    ],
                    width=600,
                    height=100,
                    background_color=ColorPalette.blue3,
                    border_radius=5,
                    border="1px solid #ccc",
                    on_click=self.go_to_camera_verification_part1,
                    alignment=Qt.AlignmentFlag.AlignCenter,
                )
            ],
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

    def on_route_popped(self):
        print("route_popped")
        self.state.update(
            timer_reached_zero=False,
            time_to_close_door_automatically=120
        )
        self.timer.start()

    def handle_timer(self):
        if self.state.time_to_close_door_automatically == 1:
            self.timer.stop()
            self.state.update(timer_reached_zero=True)
            AudioWorker.delayed(f"{self.curr_dir}/assets/door_open_idle.mp3")
            QTimer.singleShot(5 * 1000, lambda: GpioWorker.activate(self.order_intent.get_open_door_pin()))
            QTimer.singleShot(10 * 1000, lambda: self.router.off_all("welcome"))
            return

        self.state.update(
            time_to_close_door_automatically=self.state.time_to_close_door_automatically - 1
        )

    def get_timer_text(self) -> list[BuildableWidget]:
        if self.state.timer_reached_zero:
            return []

        return [
            SizedBox(height=20),
            Text(f"A porta irá fechar automaticamente em {self.state.time_to_close_door_automatically} segundo(s)...",
                 font_size=18),
        ]

