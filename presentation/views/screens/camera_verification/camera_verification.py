from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget

from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.camera import CameraWorker
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.image import ImageFromAssets
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spinner import Spinner
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from router import Router
from utils.file import FileUtils


class CameraVerification(QWidget):
    def __init__(self, router: Router, order_intent: NewOrderIntent):
        super().__init__()
        router.hide_bg()
        self.router = router
        self.order_intent = order_intent
        self.curr_dir = FileUtils.dir(__file__)

        Scaffold(
            parent=self,
            child=Column(
                children=[
                    TransparentTopBar(router, can_pop=True),
                    Column(
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
                    ),
                    ImageFromAssets(
                        path=f"{FileUtils.dir(__file__)}/assets/fila_botijoes.png",
                        size=self.router.application.primaryScreen().availableSize().width()
                    ),
                ]
            ),
        )

        AudioWorker.play(f"{self.curr_dir}/assets/audio.mp3")
        QTimer.singleShot(4000, self.verify_placed_container)

    def verify_placed_container(self):
        worker = CameraWorker(
            callback=lambda x: self.handle_camera_callback(x)
        )
        self.router.threadpool.start(worker)

    def handle_camera_callback(self, passed):
        print(f"camera result {passed}")

        if not passed:
            print(1234)
            AudioWorker.play(f"{self.curr_dir}/assets/security_check_failed.mp3")


    def go_to_camera_verification(self):
        pass