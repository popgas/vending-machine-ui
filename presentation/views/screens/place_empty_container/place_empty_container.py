import time

import pygame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget

from infrastructure.hardware.gpio import GpioWorker
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerHorizontal
from presentation.views.components.layout.spinner import Spinner
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.screens.camera_verification.camera_verification import CameraVerification
from presentation.views.screens.place_empty_container.place_empty_container_state import PlaceEmptyContainerState
from router import Router
from utils.file import FileUtils


class PlaceEmptyContainer(QWidget):
    def __init__(self, router: Router, order_intent: NewOrderIntent):
        super().__init__()
        router.hide_bg()
        self.router = router
        self.order_intent = order_intent
        self.curr_dir = FileUtils.dir(__file__)
        self.state = PlaceEmptyContainerState()

        Scaffold(
            parent=self,
            state=self.state,
            child=lambda: Column(
                children=[
                    TransparentTopBar(router, can_pop=False),
                    Column(
                        flex=1,
                        children=[
                            Text("Insira seu botijão vazio", font_size=50, color=ColorPalette.blue3),
                            SizedBox(height=20),
                            Text("Coloque seu botijão vazio na porta que se abriu e afaste-se", font_size=30,
                                 alignment=Qt.AlignmentFlag.AlignCenter),
                            SizedBox(height=40),
                            Row(
                                children=[
                                    Column(
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
                            self.get_button_or_closing_door_spinner(),
                        ],
                        alignment=Qt.AlignmentFlag.AlignCenter
                    ),
                ]
            ),
        )

        self.play_audio()
        GpioWorker.activate(self.order_intent.get_open_door_pin())

    def go_to_camera_verification_part1(self):
        self.state.update(closing_door=True)
        QTimer.singleShot(150, self.go_to_camera_verification_part2)

    def go_to_camera_verification_part2(self):
        self.play_audio2()
        GpioWorker.activate(self.order_intent.get_close_door_pin())
        QTimer.singleShot(10 * 1000, lambda: self.router.push(CameraVerification(self.router, self.order_intent)))

    def play_audio(self):
        pygame.mixer.init()
        pygame.mixer.music.load(f"{self.curr_dir}/assets/audio.mp3")
        pygame.mixer.music.play()

    def play_audio2(self):
        pygame.mixer.init()
        pygame.mixer.music.load(f"{self.curr_dir}/assets/door_will_close.mp3")
        pygame.mixer.music.play()

    def get_button_or_closing_door_spinner(self):
        if self.state.closing_door:
            return Column(
                children=[
                    Spinner(size=70),
                    Text("Fechando porta, aguarde por favor",
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
