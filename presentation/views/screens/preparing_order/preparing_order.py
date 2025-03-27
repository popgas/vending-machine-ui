from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget

from domains.enums.machine_doors import VendingMachinePins
from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.gpio import GpioWorker
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.image import ImageFromAssets
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spinner import Spinner
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from application import Application
from utils.file import FileUtils


class PreparingOrderScreen(QWidget):
    def __init__(self, router: Application, order_intent: NewOrderIntent):
        super().__init__()
        self.router = router
        self.curr_dir = FileUtils.dir(__file__)
        self.order_intent = order_intent

        Scaffold(
            parent=self,
            child=Column(
                children=[
                    Row(
                        content_margin=30,
                        children=[
                            TransparentTopBar(router, can_pop=False),
                        ]
                    ),
                    Text("Preparando botijão", font_size=50, color=ColorPalette.blue3),
                    SizedBox(height=20),
                    Text("Aguarde um momento enquanto preparamos o seu botijão 13kg cheio.", font_size=30,
                         alignment=Qt.AlignmentFlag.AlignCenter),
                    SizedBox(height=40),
                    Spinner(size=120),
                    SizedBox(height=40),
                    ImageFromAssets(
                        path=f"./assets/images/fila_botijoes.png",
                        width=self.router.application.primaryScreen().availableSize().width()
                    ),
                ]
            ),
        )

        AudioWorker.delayed(f"{self.curr_dir}/assets/payment_received.mp3")
        QTimer.singleShot(150, lambda: GpioWorker.activate(VendingMachinePins.rotateCarrousel))
        QTimer.singleShot(10 * 1000, self.ready_to_pick)

    def ready_to_pick(self):
        AudioWorker.play(f"{self.curr_dir}/assets/ready_to_pickup.mp3")
        QTimer.singleShot(5 * 1000, lambda: GpioWorker.activate(self.order_intent.get_open_door_pin()))
        QTimer.singleShot(10 * 1000, lambda: self.router.push('order_completed', self.order_intent))