import tkinter as tk

from application import Application
from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.gpio import GpioWorker
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.enums.alignment import Fill, Anchor, Side
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets, CircularSpinner
from presentation.views.components.layout.padding import Padding
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerVertical
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.screens.place_empty_container.place_empty_container_state import PlaceEmptyContainerState
from utils.file import FileUtils


class PlaceEmptyContainerScreen(tk.Frame):
    def __init__(self, app: Application, order_intent: NewOrderIntent):
        super().__init__(app.container, bg="#ECEFF1")
        self.app = app
        self.order_intent = order_intent
        self.curr_dir = FileUtils.dir(__file__)
        self.state = PlaceEmptyContainerState()
        self.app.after(1000, self.handle_timer)
        # self.timer = QTimer()
        # self.timer.setInterval(1000)
        # self.timer.timeout.connect(self.handle_timer)
        # self.timer.start()

        Scaffold(
            parent=self,
            state=self.state,
            child=lambda: Column(
                padding=Padding.all(30),
                expand=True,
                children=[
                    TransparentTopBar(app, can_pop=False),
                    Column(
                        expand=True,
                        children=[
                            SpacerVertical(),
                            Text("Insira seu botijão vazio", font_size=40, color=ColorPalette.blue3),
                            SizedBox(height=20),
                            Text("Coloque seu botijão vazio na porta que se abriu e afaste-se", font_size=25),
                            *self.get_timer_text(),
                            SizedBox(height=30),
                            Column(
                                expand=True,
                                children=[
                                    Row(
                                        children=[
                                            ImageFromAssets(
                                                path=f"{self.curr_dir}/assets/instrucoes_colocar_botijao.png",
                                                width=int(252 * 1.1),
                                                height=int(310 * 1.1),
                                                padding=Padding.all(30),
                                            ),
                                        ],
                                        background_color="#ffffff",
                                        border_radius=10,
                                        border_color="#ccc",
                                        fill=Fill.NONE,
                                    )
                                ]
                            ),
                            SizedBox(height=40),
                            self.get_button_or_closing_door_spinner(),
                        ],
                        # alignment=Qt.AlignmentFlag.AlignCenter
                    ),
                ]
            ),
        )

        AudioWorker.play(f"{self.curr_dir}/assets/audio.mp3")
        GpioWorker.activate(self.order_intent.get_open_door_pin())

    def go_to_camera_verification_part1(self):
        self.state.update(closing_door=True, timer_reached_zero=True)
        self.app.after(150, self.go_to_camera_verification_part2)

    def go_to_camera_verification_part2(self):
        AudioWorker.play(f"{self.curr_dir}/assets/door_will_close.mp3")
        self.app.after(5 * 1000, lambda: GpioWorker.activate(self.order_intent.get_close_door_pin()))
        self.app.after(10 * 1000, self.go_to_camera_verification_part3)

    def go_to_camera_verification_part3(self):
        self.state.update(closing_door=False)
        self.app.push('camera_verification', self.order_intent)

    def get_button_or_closing_door_spinner(self):
        if self.state.closing_door:
            return Column(
                padding=Padding(bottom=30),
                children=[
                    CircularSpinner(root=self.app, side=Side.TOP, anchor=Anchor.CENTER),
                    SizedBox(height=20),
                    Text("Fechando porta, afaste-se por favor!",
                         font_size=30,
                         # alignment=Qt.AlignmentFlag.AlignCenter,
                         color="#333"),
                ]
            )

        return Column(
            children=[
                Row(
                    children=[
                        Text("Pronto. Já coloquei meu botijão",
                             font_size=20,
                             padding=Padding.all(30),
                             side=Side.LEFT,
                             anchor=Anchor.LEFT,
                             color="#fff"),
                        Icon("arrow-right-white", anchor=Anchor.RIGHT, width=30, height=34, padding=Padding.all(30)),
                    ],
                    background_color=ColorPalette.blue3,
                    border_radius=5,
                    border_color="#ccc",
                    fill=Fill.NONE,
                    on_click=self.go_to_camera_verification_part1,
                )
            ],
        )

    def on_route_popped(self):
        print("route_popped")
        self.state.update(
            timer_reached_zero=False,
            time_to_close_door_automatically=120
        )
        self.handle_timer()

    def handle_timer(self):
        if self.state.timer_reached_zero:
            return

        if self.state.time_to_close_door_automatically == 1:
            self.state.update(timer_reached_zero=True)
            AudioWorker.play(f"{self.curr_dir}/assets/door_open_idle.mp3")
            self.app.after(5 * 1000, lambda: GpioWorker.activate(self.order_intent.get_open_door_pin()))
            # QTimer.singleShot(5 * 1000, lambda: GpioWorker.activate(self.order_intent.get_open_door_pin()))
            self.app.after(10 * 1000, lambda: self.app.off_all("welcome"))
            return

        self.state.update(
            time_to_close_door_automatically=self.state.time_to_close_door_automatically - 1
        )
        self.app.after(1000, self.handle_timer)

    def get_timer_text(self) -> list[BuildableWidget]:
        if self.state.timer_reached_zero:
            return []

        return [
            SizedBox(height=20),
            Text(f"A porta irá fechar automaticamente em {self.state.time_to_close_door_automatically} segundo(s)...",
                 font_size=15),
        ]

