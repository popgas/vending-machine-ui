import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget

from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.camera import CameraWorker
from infrastructure.hardware.gpio import GpioWorker
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spinner import Spinner
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.screens.camera_verification.camera_verification_state import CameraVerificationState
from application import Application
from utils.file import FileUtils


class CameraVerificationScreen(QWidget):
    def __init__(self, router: Application, order_intent: NewOrderIntent):
        super().__init__()
        router.hide_bg()
        self.router = router
        self.order_intent = order_intent
        self.curr_dir = FileUtils.dir(__file__)
        self.state = CameraVerificationState()

        Scaffold(
            parent=self,
            state=self.state,
            child=lambda: Column(
                children=[
                    Row(
                        content_margin=30,
                        children=[
                            TransparentTopBar(router, can_pop=False),
                        ]
                    ),
                    self.get_screen_content(),
                    ImageFromAssets(
                        path=f"./assets/images/fila_botijoes.png",
                        width=self.router.application.primaryScreen().availableSize().width()
                    ),
                ]
            ),
        )

        AudioWorker.play(f"{self.curr_dir}/assets/audio.mp3")
        QTimer.singleShot(4000, self.verify_placed_container)

    def get_screen_content(self):
        if self.state.failed_security_check:
            return Column(
                flex=1,
                children=[
                    Icon("fa6s.circle-exclamation",
                         width=70,
                         color="#cd5c5c"
                         ),
                    SizedBox(height=20),
                    Text("Botião Reprovado", font_size=50, color=ColorPalette.blue3),
                    SizedBox(height=20),
                    Text("Infelizmente seu botijão vazio não passou em nossa verificação de segurança.", font_size=30,
                         alignment=Qt.AlignmentFlag.AlignCenter),
                ],
                alignment=Qt.AlignmentFlag.AlignCenter
            )

        return Column(
            flex=1,
            children=[
                Text("Analisando seu botijão", font_size=50, color=ColorPalette.blue3),
                SizedBox(height=20),
                Text("Estamos verificando o estado do seu botijão. Por favor, aguarde.", font_size=30,
                     alignment=Qt.AlignmentFlag.AlignCenter),
                SizedBox(height=40),
                Spinner(size=120),
            ],
            alignment=Qt.AlignmentFlag.AlignCenter
        )

    def verify_placed_container(self):
        self.router.push("payment_selection", self.order_intent)
        return
        worker = CameraWorker( )
        worker.signals.result.connect(lambda x: self.handle_camera_callback(x))

        self.app.threadpool.start(worker)

    def handle_camera_callback(self, passed):
        print(f"camera result {passed}")

        if not passed:
            self.state.update(failed_security_check=True)
            QTimer.singleShot(150, self.validation_failed)

    def validation_failed(self):
        AudioWorker.play(f"{self.curr_dir}/assets/security_check_failed.mp3")
        GpioWorker.activate(self.order_intent.get_open_door_pin())
        QTimer.singleShot(10 * 1000, lambda: self.router.pop())

    def go_to_camera_verification(self):
        pass
