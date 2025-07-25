import base64
import os
import tkinter as tk

import cv2

from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.camera import CameraWorker, CameraResult
from infrastructure.hardware.gpio import GpioWorker
from infrastructure.http.popgas_api import PopGasApi
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.enums.alignment import Side, Anchor
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets, CircularSpinner
from presentation.views.components.layout.padding import Padding
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerVertical
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.state_provider import StateProvider
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.components.state.countdown_timer import CountdownTimer
from presentation.views.screens.camera_verification.camera_verification_state import CameraVerificationState
from application import Application
from utils.file import FileUtils
from infrastructure.observability.logger import Logger


class CameraVerificationScreen(tk.Frame):
    def __init__(self, app: Application, order_intent: NewOrderIntent):
        super().__init__(app.container, bg="#FFFFFF")
        self.app = app
        self.logger = Logger.get_logger()
        self.order_intent = order_intent
        self.curr_dir = FileUtils.dir(__file__)
        self.state = CameraVerificationState()
        self.countdown_timer = CountdownTimer(
            app=app,
            initial_value=10,
            on_reached_zero=self.app.pop,
            padding=Padding(top=25, bottom=10),
            text_builder=lambda v: f"Aguarde {v} segundo(s)...",
            autostart=False
        )

        StateProvider(
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
                    SpacerVertical(),
                    Icon("circle-exclamation-red",
                         width=70,
                         height=70,
                         side=Side.TOP,
                         anchor=Anchor.CENTER,
                     ),
                    SizedBox(height=20),
                    Text("Botijão Reprovado", font_size=35, color=ColorPalette.blue3),
                    SizedBox(height=40),
                    Text("Infelizmente seu botijão vazio não", font_size=22),
                    Text("passou em nossa verificação de segurança.", font_size=22),
                    SizedBox(height=100),
                    self.countdown_timer,
                    SpacerVertical(),
                ],
            )

        return Column(
            expand=True,
            children=[
                SpacerVertical(),
                Text("Analisando seu botijão", font_size=40, color=ColorPalette.blue3),
                SizedBox(height=20),
                Text("Estamos verificando o estado do seu botijão.", font_size=25),
                Text("Por favor, aguarde.", font_size=25),
                SizedBox(height=40),
                CircularSpinner(root=self.app, side=Side.TOP, anchor=Anchor.CENTER),
                SpacerVertical(),
            ],
        )

    def verify_placed_container(self):
        try:
            CameraWorker.start(
                camera_socket=self.order_intent.get_camera(),
                on_completed=self.handle_camera_callback
            )
        except Exception as e:
            self.handle_camera_callback(CameraResult(error=True))


    def handle_camera_callback(self, result: CameraResult):
        if result.error:
            AudioWorker.play(f"{self.curr_dir}/assets/camera_not_working.mp3")
            GpioWorker.activate(self.order_intent.get_refill_open_door_pin())
            self.app.after(10000, lambda: self.app.pop())
            return

        success, buffer = cv2.imencode('.jpg', result.taken_photo)

        if not success:
            raise RuntimeError("Falha ao codificar o frame em JPEG")

        jpg_bytes = buffer.tobytes()
        b64_str = base64.b64encode(jpg_bytes).decode('utf-8')

        # Monta o Data URI
        base64_image = f"data:image/jpeg;base64,{b64_str}"

        response = PopGasApi.request('POST', '/vending-machine-orders/verify-photo', json={
            'vending_machine_id': os.environ['VENDING_MACHINE_ID'],
            'base64_image': base64_image,
            'camera': self.order_intent.get_camera_describer(),
        }).json()

        self.logger.info(f"security check response {response}")

        if bool(response['passed_verification']):
            self.app.push("payment_selection", self.order_intent.copy_with(
                placedContainerPhoto=result.taken_photo
            ))
        else:
            self.security_check_failed()

    def security_check_failed(self):
        print("failed verification")
        self.state.update(failed_security_check=True)
        self.app.after(150, self.validation_failed)

    def validation_failed(self):
        AudioWorker.play(f"{self.curr_dir}/assets/security_check_failed.mp3")
        GpioWorker.activate(self.order_intent.get_refill_open_door_pin())
        self.countdown_timer.start()