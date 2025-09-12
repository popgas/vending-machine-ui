import os
import tkinter

from application import Application
from domains.enums.order_product_selected import OrderProductSelected
from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.gpio import GpioWorker
from infrastructure.http.popgas_api import PopGasApi
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.enums.alignment import Side, Anchor, Fill
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets, CircularSpinner, QrCodeFromString
from presentation.views.components.layout.padding import Padding
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerVertical
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.state_provider import StateProvider
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.components.state.countdown_timer import CountdownTimer
from presentation.views.screens.card_machine.card_machine_state import CardMachineState
from utils.file import FileUtils


class CardMachineScreen(tkinter.Frame):
    def __init__(self, app: Application, order_intent: NewOrderIntent):
        super().__init__(app.container, bg="#FFFFFF")
        self.curr_dir = FileUtils.dir(__file__)
        self.order_intent = order_intent
        self.app = app
        self.state = CardMachineState()
        self.correlation_id = None
        self.order_id = None
        self.idleTimer = None
        self.pix_qr_code = None

        self.countdown_timer = CountdownTimer(
            app=app,
            initial_value=7,
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
                    *self.get_content(),
                    SizedBox(height=40),
                    ImageFromAssets(
                        path=f"./assets/images/fila_botijoes.png",
                        width=self.app.container.winfo_width(),
                        height=int((self.app.container.winfo_width() / 2.91)),
                    ),
                ]
            ),
        )

        self.app.after(200, self.create_order_request)

    def play_initial_audio(self):
        if self.order_intent.paymentMethodId == 5 or self.order_intent.paymentMethodId == 9:
            if self.pix_qr_code is not None:
                AudioWorker.play(f"{self.curr_dir}/assets/pay_with_qr_code_screen.mp3")
            else:
                AudioWorker.play(f"{self.curr_dir}/assets/pay_with_qr_code_machine.mp3")
        else:
            AudioWorker.play(f"{self.curr_dir}/assets/audio.mp3")

    def get_payment_text(self) -> list[BuildableWidget]:
        if self.is_pix():
            if self.pix_qr_code is not None:
                return [
                    Text("Escaneie o QR code para fazer o pagamento", font_size=22),
                ]
            else:
                return [
                    Text("Escaneie o QR code na tela da maquininha", font_size=22),
                    Text("de cartão para efetuar o pagamento", font_size=22),
                ]
        else:
            return [
                Text("Insira ou aproxime seu cartão na maquininha", font_size=22),
            ]

    def is_pix(self):
        return self.order_intent.paymentMethodId == 5 or self.order_intent.paymentMethodId == 9

    def get_content(self) -> list[BuildableWidget]:
        if self.state.rejected:
            return [
                SpacerVertical(),
                Icon("circle-exclamation-red", width=70, height=70, side=Side.TOP, anchor=Anchor.CENTER),
                SizedBox(height=20),
                Text("Pagamento Recusado", font_size=35, color=ColorPalette.blue3),
                SizedBox(height=20),
                Text("O pagamento foi cancelado ou recusado.", font_size=22),
                SizedBox(height=50),
                self.countdown_timer,
                SpacerVertical(),
            ]

        return [
            SpacerVertical(),
            Text("Aguardando pagamento", font_size=35, color=ColorPalette.blue3),
            SizedBox(height=20),
            *self.get_payment_text(),
            SizedBox(height=40),
            *self.get_pix_qr_code_or_billing_machine(),
            SizedBox(height=40),
            *self.get_cancel_button(),
            SizedBox(height=40),
            SpacerVertical(),
        ]

    def get_cancel_button(self) -> list[BuildableWidget]:
        if not self.is_pix():
            return []

        return [
            Row(
                expand=True,
                side=Side.TOP,
                fill=Fill.NONE,
                children=[
                    Row(
                        width=450,
                        height=100,
                        children=[
                            SizedBox(width=30),
                            Icon("xmark-white",
                                 side=Side.LEFT,
                                 anchor=Anchor.RIGHT,
                                 width=30,
                                 height=40,
                                 padding=Padding(0, 20, 15, 15)),
                            SizedBox(width=20),
                            Text("Cancelar Operação",
                                 font_size=24,
                                 side=Side.LEFT,
                                 anchor=Anchor.RIGHT,
                                 color="#fff"),
                        ],
                        background_color="#cd5c5c",
                        border_radius=8,
                        fill=Fill.X,
                        border_color="#ccc",
                        on_click=self.cancel_operation,
                    ),
                ],
            ),
        ]

    def cancel_operation(self):
        PopGasApi.request('DELETE', f'/vending-machine-orders/{self.order_id}')

        self.cancel_idle_timer()
        self.app.pop()

    def get_pix_qr_code_or_billing_machine(self) -> list[BuildableWidget]:
        if self.pix_qr_code is not None:
            return [
                QrCodeFromString(
                    qrcode_string=self.pix_qr_code,
                    width=250,
                    height=250,
                    side=Side.TOP,
                    anchor=Anchor.CENTER,
                ),
                SpacerVertical(),
                CircularSpinner(root=self.app, side=Side.TOP, anchor=Anchor.CENTER),
            ]

        return [
            ImageFromAssets(
                path=f"{self.curr_dir}/assets/billing-machine.png",
                width=150,
                height=150,
                side=Side.TOP,
                anchor=Anchor.CENTER,
            ),
            SpacerVertical(),
            CircularSpinner(root=self.app, side=Side.TOP, anchor=Anchor.CENTER),
        ]

    def create_order_request(self):
        if self.order_intent.productSelected == OrderProductSelected.onlyGasRefill:
            product_selected = 'ONLY_GAS_REFILL'
        else:
            product_selected = 'GAS_WITH_CONTAINER'

        vm_id = os.environ['VENDING_MACHINE_ID']

        response = PopGasApi.request('POST', '/vending-machine-orders', json={
            'vending_machine_id': vm_id,
            'payment_method_id': self.order_intent.paymentMethodId,
            'product_price': self.order_intent.selectedPaymentMethodPrice,
            'product_selected': product_selected,
            # 'placed_container_photo': self.order_intent.get_placed_container_photo_as_base64(),
            # 'purchased_container_photo': self.order_intent.get_purchased_container_photo_as_base64(),
        }).json()

        print(f"creating order response {response}")

        self.pix_qr_code = str(response['pix_qr_code']) if response['pix_qr_code'] is not None else None
        self.correlation_id = str(response['correlation_id'])
        self.order_id = str(response['id'])
        self.check_order_payment_status()

        self.idleTimer = self.app.after(300 * 1000, lambda: self.handle_payment_rejected())
        self.play_initial_audio()
        self.state.notify()

    def check_order_payment_status(self):
        try:
            if not self.state.awaiting_payment_approval:
                return

            print("Checking payment status")
            response = PopGasApi.request('GET', f"/vending-machine-orders/{self.correlation_id}").json()
            print(f"checking order response {response}")

            status = str(response['payment_status'])
            flow_status = str(response['flow_status'])

            match status:
                case 'APPROVED':
                    self.cancel_idle_timer()
                    self.state.update(awaiting_payment_approval=False)
                    self.app.push('preparing_order', self.order_intent.copy_with(
                        correlationId=self.correlation_id,
                    ))
                    return
                case 'REJECTED' | 'UNAUTHORIZED' | 'ABORTED' | 'CANCELLED':
                    self.cancel_idle_timer()
                    self.handle_payment_rejected()
                    return

            if flow_status == 'ORDER_VALIDATION_FAILED':
                self.state.update(awaiting_payment_approval=False)
                self.cancel_idle_timer()
                self.card_machine_unreachable()
                return

            if self.state.awaiting_payment_approval:
                self.app.after(3000, self.check_order_payment_status)
        except Exception as e:
            self.app.after(3000, self.check_order_payment_status)

    def cancel_idle_timer(self):
        if self.idleTimer is not None:
            self.app.after_cancel(self.idleTimer)

    def handle_payment_rejected(self):
        self.state.update(
            awaiting_payment_approval=False,
            rejected=True
        )
        AudioWorker.play(f"{self.curr_dir}/assets/payment_rejected.mp3")
        self.app.after(5 * 1000, lambda: self.app.pop())

    def card_machine_unreachable(self):
        AudioWorker.play(f"{self.curr_dir}/assets/card_machine_disconnected.mp3")
        self.state.update(awaiting_payment_approval=False)

        if self.order_intent.productSelected == OrderProductSelected.onlyGasRefill:
            self.app.after(5 * 5000, lambda: self.card_machine_unreachable_part_2())
        else:
            self.app.after(5 * 5000, lambda: self.app.off_all("welcome"))

    def card_machine_unreachable_part_2(self):
        AudioWorker.play(f"{self.curr_dir}/assets/error_take_back_empty_container.mp3")

        self.app.after(5 * 1000, lambda: GpioWorker.activate(self.order_intent.get_refill_open_door_pin()))
        self.app.after(10 * 1000, lambda: self.app.off_all("welcome"))
