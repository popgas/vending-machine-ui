import tkinter

from application import Application
from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.gpio import GpioWorker
from infrastructure.http.popgas_api import PopGasApi
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.buttons.blue_button import BlueButton
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.enums.alignment import Side, Anchor, Fill
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets, CircularSpinner
from presentation.views.components.layout.padding import Padding
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerVertical
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.state_provider import StateProvider
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.screens.order_completed.order_completed_state import OrderCompletedState
from utils.file import FileUtils


class OrderCompletedScreen(tkinter.Frame):
    def __init__(self, app: Application, order_intent: NewOrderIntent):
        super().__init__(app.container, bg="#FFFFFF")
        self.app = app
        self.order_intent = order_intent
        self.curr_dir = FileUtils.dir(__file__)
        self.state = OrderCompletedState()

        StateProvider(
            parent=self,
            state=self.state,
            child=lambda: Column(
                expand=True,
                children=[
                    Column(children=[
                        TransparentTopBar(app, can_pop=False),
                    ]),
                    SpacerVertical(),
                    ImageFromAssets(
                        path=f"{self.curr_dir}/assets/confetti.png",
                        width=130,
                        height=130,
                        side=Side.TOP,
                        anchor=Anchor.CENTER
                    ),
                    SizedBox(height=20),
                    Text("Obrigado pela compra", font_size=35, color=ColorPalette.blue3),
                    SizedBox(height=60),
                    *self.get_rating_component(),
                    *self.closing_doors_components(),
                    SizedBox(height=40),
                    SpacerVertical(),
                    *self.get_go_back_button(),
                ],
            ),
        )

        AudioWorker.play(f"{self.curr_dir}/assets/thanks_and_rate.mp3")
        self.timer = self.app.after(60 * 1000, self.close_door_and_go_back_to_beginning)

    def get_go_back_button(self) -> list[BuildableWidget]:
        if self.state.closing_doors:
            return []

        return [
            Column(
                width=500,
                height=100,
                fill=Fill.NONE,
                expand=False,
                children=[
                    BlueButton(
                        label="Voltar ao Ínicio",
                        font_size=30,
                        on_click=lambda: self.close_door_and_go_back_to_beginning(),
                    ),
                ]
            )
        ]

    def closing_doors_components(self) -> list[BuildableWidget]:
        if self.state.closing_doors:
            return [
                SpacerVertical(),
                CircularSpinner(root=self.app, side=Side.TOP, anchor=Anchor.CENTER),
                SizedBox(height=20),
                Text("Fechando portas...", font_size=20)
            ]

        return []

    def get_rating_component(self) -> list[BuildableWidget]:
        if not self.state.has_rated:
            return [
                Column(
                    width=int(self.app.container.winfo_width() * 0.9),
                    height=250,
                    fill=Fill.NONE,
                    expand=False,
                    children=[
                        Column(
                            padding=Padding.all(30),
                            children=[
                                Text("Avalie a sua experiência", font_size=25, color=ColorPalette.blue3),
                                SizedBox(height=40),
                                Row(
                                    children=[
                                        self.get_rate_button("rate_1.png", "Muito Ruim", 1),
                                        self.get_rate_button("rate_2.png", "Ruim", 2),
                                        self.get_rate_button("rate_3.png", "Neutro", 3),
                                        self.get_rate_button("rate_4.png", "Boa", 4),
                                        self.get_rate_button("rate_5.png", "Muito Boa", 5),
                                    ]
                                )
                            ]
                        )
                    ],
                    background_color="#fff",
                    border_radius=8,
                    border_color="#888",
                )
            ]

        return [
            Column(
                width=int(self.app.container.winfo_width() * 0.8),
                height=250,
                fill=Fill.NONE,
                expand=False,
                children=[
                    Column(
                        children=[
                            Column(
                                padding=Padding.all(20),
                                children=[
                                    Text("Seu feedback foi enviado, muito obrigado!", font_size=22,
                                         color=ColorPalette.blue3),
                                    SizedBox(height=35),
                                    Icon("circle-check-green", width=70, height=70, side=Side.TOP, anchor=Anchor.CENTER),
                                ],
                            )
                        ],
                        background_color="#fff",
                        border_radius=8,
                        border_color="#888",
                    )
                ]
            )
        ]

    def get_rate_button(self, image, title, rating_score):
        return Column(
            expand=True,
            fill=Fill.X,
            side=Side.LEFT,
            children=[
                ImageFromAssets(
                    path=f"{self.curr_dir}/assets/{image}",
                    width=40,
                    height=40,
                    side=Side.TOP,
                    anchor=Anchor.CENTER,
                ),
                SizedBox(height=12),
                Text(title, font_size=15)
            ],
            on_click=lambda: self.update_rating_score(rating_score),
        )

    def update_rating_score(self, rating_score):
        AudioWorker.stop()

        PopGasApi.request("PUT", f"/vending-machine-orders/{self.order_intent.correlationId}/rating", json={
            'rating': rating_score,
        })

        self.state.update(has_rated=True)

        self.app.after(5000, self.close_door_and_go_back_to_beginning)

    def close_door_and_go_back_to_beginning(self):
        self.app.after_cancel(self.timer)
        self.state.update(closing_doors=True)

        AudioWorker.play(f"{self.curr_dir}/assets/closing_doors.mp3")
        GpioWorker.activate(self.order_intent.get_full_container_close_door_pin())

        self.app.after(15 * 1000, lambda: self.app.off_all("welcome"))
