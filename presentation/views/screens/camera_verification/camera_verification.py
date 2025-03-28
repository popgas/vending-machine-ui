import tkinter as tk

from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.camera import CameraWorker, CameraResult
from infrastructure.hardware.gpio import GpioWorker
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.enums.alignment import Side, Anchor
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets, CircularSpinner
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerVertical
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.screens.camera_verification.camera_verification_state import CameraVerificationState
from application import Application
from utils.file import FileUtils


class CameraVerificationScreen(tk.Frame):
    def __init__(self, app: Application, order_intent: NewOrderIntent):
        super().__init__(app.container, bg="#ECEFF1")
        self.app = app
        self.order_intent = order_intent
        self.curr_dir = FileUtils.dir(__file__)
        self.state = CameraVerificationState()
        print(self.app.container.winfo_width())

        Scaffold(
            parent=self,
            state=self.state,
            child=lambda: Column(
                expand=True,
                children=[
                    Column(children=[
                        TransparentTopBar(app, can_pop=False),
                    ]),
                    self.get_screen_content(),
                    ImageFromAssets(
                        path=f"{FileUtils.root()}/assets/images/fila_botijoes.png",
                        width=self.app.container.winfo_width(),
                        height=int((self.app.container.winfo_width() / 2.91)),
                    ),
                ]
            ),
        )

        AudioWorker.play(f"{self.curr_dir}/assets/audio.mp3")
        app.after(4000, self.verify_placed_container)

    def get_screen_content(self):
        if self.state.failed_security_check:
            return Column(
                expand=True,
                children=[
                    Icon("fa6s.circle-exclamation",
                         width=70,
                         color="#cd5c5c"
                         ),
                    SizedBox(height=20),
                    Text("Botião Reprovado", font_size=50, color=ColorPalette.blue3),
                    SizedBox(height=20),
                    Text("Infelizmente seu botijão vazio não passou em nossa verificação de segurança.", font_size=30),
                ],
            )

        return Column(
            expand=True,
            children=[
                SpacerVertical(),
                Text("Analisando seu botijão", font_size=40, color=ColorPalette.blue3),
                SizedBox(height=20),
                Text("Estamos verificando o estado do seu botijão. Por favor, aguarde.", font_size=25),
                SizedBox(height=40),
                CircularSpinner(root=self.app, side=Side.TOP, anchor=Anchor.CENTER),
                SpacerVertical(),
            ],
        )

    def verify_placed_container(self):
        CameraWorker.start(on_completed=self.handle_camera_callback)

    def handle_camera_callback(self, result: CameraResult):
        if result.best_score >= 50:
            self.app.push("payment_selection", self.order_intent)
        else:
            self.state.update(failed_security_check=True)
            self.app.after(150, self.validation_failed)

    def validation_failed(self):
        AudioWorker.play(f"{self.curr_dir}/assets/security_check_failed.mp3")
        GpioWorker.activate(self.order_intent.get_open_door_pin())
        self.app.after(10 * 1000, lambda: self.app.pop())