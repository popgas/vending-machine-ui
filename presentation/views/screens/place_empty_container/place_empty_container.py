import tkinter as tk

from application import Application
from domains.enums.machine_doors import VendingMachinePins
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
from presentation.views.components.scaffold.state_provider import StateProvider
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.components.state.countdown_timer import CountdownTimer
from presentation.views.screens.place_empty_container.place_empty_container_state import PlaceEmptyContainerState
from utils.file import FileUtils


class PlaceEmptyContainerScreen(tk.Frame):
    def __init__(self, app: Application, order_intent: NewOrderIntent):
        super().__init__(app.container, bg="#FFFFFF")
        self.app = app
        self.order_intent = order_intent
        self.curr_dir = FileUtils.dir(__file__)
        self.state = PlaceEmptyContainerState()

        self.countdown_timer = CountdownTimer(
            app=app,
            initial_value=120,
            on_reached_zero=self.on_reached_zero_countdown,
            padding=Padding(top=25, bottom=10),
            text_builder=lambda v: f"A porta irá fechar automaticamente em {v} segundo(s)..."
        )

        StateProvider(
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
                            Text("Insira seu botijão vazio", font_size=32, color=ColorPalette.blue3),
                            SizedBox(height=20),
                            Text("Coloque seu botijão vazio na porta", font_size=25),
                            Text(" que se abriu e afaste-se", font_size=25),
                            self.get_timer_text(),
                            SizedBox(height=50),
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
                            *self.get_button_or_closing_door_spinner(),
                        ],
                    ),
                ]
            ),
        )

        AudioWorker.play(f"{self.curr_dir}/assets/audio.mp3")
        GpioWorker.activate(self.order_intent.get_refill_open_door_pin())

    def go_to_camera_verification_part1(self):
        self.state.update(closing_door=True, timer_reached_zero=True)
        self.app.after(150, self.go_to_camera_verification_part2)

    def go_to_camera_verification_part2(self):
        AudioWorker.play(f"{self.curr_dir}/assets/door_will_close.mp3")
        self.app.after(5 * 1000, lambda: GpioWorker.close_all_doors())
        self.app.after(7 * 1000, self.go_to_camera_verification_part3)

    def go_to_camera_verification_part3(self):
        self.state.update(closing_door=False)
        self.app.push('camera_verification', self.order_intent)

    def get_button_or_closing_door_spinner(self) -> list[BuildableWidget]:
        if self.state.cancelling:
            return [
                CircularSpinner(root=self.app, side=Side.TOP, anchor=Anchor.CENTER),
                SizedBox(height=20),
                Text("Cancelando operação",
                     font_size=27,
                     color="darkred"),
                SizedBox(height=10),
                Text("Iremos fechar a porta, afaste-se por favor!",
                     font_size=22,
                     color="#333"),
                SpacerVertical(),
            ]

        if self.state.closing_door:
            return [
                CircularSpinner(root=self.app, side=Side.TOP, anchor=Anchor.CENTER),
                SizedBox(height=20),
                Text("Fechando porta, afaste-se por favor!",
                     font_size=25,
                     color="#333"),
                SpacerVertical(),
            ]

        return [
            SpacerVertical(),
            Column(
                children=[
                    Text("Pronto. Já coloquei meu botijão",
                         font_size=20,
                         padding=Padding.all(50),
                         side=Side.LEFT,
                         anchor=Anchor.LEFT,
                         color="#fff"),
                    Icon("arrow-right-white",
                         anchor=Anchor.RIGHT,
                         side=Side.RIGHT,
                         width=30,
                         height=34,
                         padding=Padding.all(50)),
                ],
                background_color=ColorPalette.blue3,
                border_radius=5,
                border_color="#ccc",
                on_click=self.go_to_camera_verification_part1,
            ),

            SizedBox(height=60),

            Column(
                children=[
                    Text("Cancelar Operação",
                         font_size=20,
                         padding=Padding(50, 0, 15, 15),
                         side=Side.LEFT,
                         anchor=Anchor.LEFT,
                         color="#fff"),
                    Icon("xmark-white",
                         anchor=Anchor.RIGHT,
                         side=Side.RIGHT,
                         width=30,
                         height=40,
                         padding=Padding(0, 50, 15, 15)),
                ],
                background_color="#cd5c5c",
                border_radius=5,
                on_click=self.cancel_operation,
            )
        ]

    def cancel_operation(self):
        AudioWorker.play(f"{self.curr_dir}/assets/place_container_cancellation.mp3")
        self.state.update(cancelling=True)
        self.countdown_timer.cancel()
        self.app.after(7 * 1000, lambda: GpioWorker.activate(self.order_intent.get_refill_close_door_pin()))
        self.app.after(12 * 1000, lambda: self.app.off_all("welcome"))

    def on_route_popped(self):
        print("route_popped")
        self.countdown_timer.cancel()

    def on_reached_zero_countdown(self):
        self.state.update(timer_reached_zero=True)
        self.countdown_timer.cancel()
        AudioWorker.play(f"{self.curr_dir}/assets/door_open_idle.mp3")
        self.app.after(7 * 1000, lambda: GpioWorker.close_all_doors())
        self.app.after(12 * 1000, lambda: self.app.off_all("welcome"))

    def get_timer_text(self) -> BuildableWidget:
        if self.state.timer_reached_zero or self.state.cancelling:
            return Column(children=[])

        return self.countdown_timer
