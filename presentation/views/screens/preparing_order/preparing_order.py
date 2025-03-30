import tkinter

from application import Application
from domains.enums.machine_doors import VendingMachinePins
from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.camera import CameraWorker, CameraResult
from infrastructure.hardware.gpio import GpioWorker
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.enums.alignment import Side, Anchor
from presentation.views.components.layout.image import ImageFromAssets, CircularSpinner
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerVertical
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.state_provider import StateProvider
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from utils.file import FileUtils


class PreparingOrderScreen(tkinter.Frame):
    def __init__(self, app: Application, order_intent: NewOrderIntent):
        super().__init__(app.container, bg="#ECEFF1")
        self.app = app
        self.curr_dir = FileUtils.dir(__file__)
        self.order_intent = order_intent

        StateProvider(
            parent=self,
            child=Column(
                expand=True,
                children=[
                    Column(children=[
                        TransparentTopBar(app, can_pop=False),
                    ]),
                    SpacerVertical(),
                    Text("Preparando botijão", font_size=40, color=ColorPalette.blue3),
                    SizedBox(height=20),
                    Text("Aguarde um momento enquanto", font_size=25),
                    Text("preparamos o seu botijão 13kg cheio.", font_size=25),
                    SizedBox(height=40),
                    CircularSpinner(root=self.app, side=Side.TOP, anchor=Anchor.CENTER),
                    SpacerVertical(),
                    ImageFromAssets(
                        path=f"./assets/images/fila_botijoes.png",
                        width=self.app.container.winfo_width(),
                        height=int((self.app.container.winfo_width() / 2.91)),
                    ),
                ]
            ),
        )

        AudioWorker.play(f"{self.curr_dir}/assets/payment_received.mp3")
        self.app.after(150, lambda: GpioWorker.activate(VendingMachinePins.rotateCarrousel))
        self.app.after(6 * 1000, self.take_security_photo)

    def take_security_photo(self):
        CameraWorker.start(
            camera_socket=self.order_intent.get_camera(),
            on_completed=self.ready_to_pick
        )

    def ready_to_pick(self, camera_result: CameraResult):
        AudioWorker.play(f"{self.curr_dir}/assets/ready_to_pickup.mp3")
        self.app.after(5 * 1000, lambda: GpioWorker.activate(self.order_intent.get_open_door_pin()))
        self.app.after(10 * 1000, lambda: self.app.push('order_completed', self.order_intent.copy_with(
            purchasedContainerPhoto=camera_result.taken_photo
        )))