import os
import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget

from domains.enums.order_product_selected import OrderProductSelected
from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.gpio import GpioWorker
from infrastructure.http.popgas_api import PopGasApi
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spinner import Spinner
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.scaffold import Scaffold
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from presentation.views.screens.card_machine.card_machine_state import CardMachineState
from router import Router
from utils.file import FileUtils


class CardMachineScreen(QWidget):
    def __init__(self, router: Router, order_intent: NewOrderIntent):
        super().__init__()
        router.hide_bg()
        self.curr_dir = FileUtils.dir(__file__)
        self.order_intent = order_intent
        self.play_initial_audio()
        self.router = router
        self.state = CardMachineState()
        self.correlation_id = None
        self.timer = QTimer()
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.check_order_payment_status)

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
                    Column(
                        flex=1,
                        children=[
                            *self.get_content(),
                            SizedBox(height=40),
                            ImageFromAssets(
                                path=f"./assets/images/fila_botijoes.png",
                                size=self.router.application.primaryScreen().availableSize().width()
                            ),
                        ],
                        alignment=Qt.AlignmentFlag.AlignCenter
                    ),
                ]
            ),
        )

        self.create_order_request()

    def play_initial_audio(self):
        if self.order_intent.paymentMethodId == 5 or self.order_intent.paymentMethodId == 9:
            AudioWorker.delayed(f"{self.curr_dir}/assets/pay_with_qr_code.mp3")
        else:
            AudioWorker.delayed(f"{self.curr_dir}/assets/audio.mp3")

    def get_payment_text(self) -> str:
        if self.order_intent.paymentMethodId == 5 or self.order_intent.paymentMethodId == 9:
            return "Escaneie o QR code na tela da maquininha de cartão para efetuar o pagamento"
        else:
            return "Insira ou aproxime seu cartão na maquininha"

    def get_content(self) -> list[BuildableWidget]:
        if self.state.rejected:
            return [
                Icon("fa6s.circle-exclamation", size=70, color="#cd5c5c"),
                SizedBox(height=20),
                Text("Pagamento Recusado", font_size=50, color=ColorPalette.blue3),
                SizedBox(height=20),
                Text("O pagamento foi cancelado ou recusado. Tente novamente ou escolha outra forma de pagamento",
                     font_size=30,
                     alignment=Qt.AlignmentFlag.AlignCenter),
            ]

        return [
            Text("Aguardando pagamento", font_size=50, color=ColorPalette.blue3),
            SizedBox(height=20),
            Text(self.get_payment_text(), font_size=30, alignment=Qt.AlignmentFlag.AlignCenter),
            SizedBox(height=40),
            Spinner(size=120)
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
            'product_price': self.order_intent.productPrice,
            'product_selected': product_selected,
        }).json()

        print(f"creating order response {response}")

        self.correlation_id = str(response['correlation_id'])

        self.timer.start()

    def check_order_payment_status(self):
        print("Checking payment status")
        response = PopGasApi.request('GET', f"/vending-machine-orders/{self.correlation_id}").json()
        print(f"checking order response {response}")

        status = str(response['payment_status'])
        flow_status = str(response['flow_status'])

        match status:
            case 'APPROVED':
                self.timer.stop()
                self.router.push('preparing_order', self.order_intent.copy_with(
                    correlationId=self.correlation_id
                ))
                return
            case 'REJECTED' | 'UNAUTHORIZED' | 'ABORTED' | 'CANCELLED':
                self.handle_payment_rejected()
                return

        if flow_status == 'ORDER_VALIDATION_FAILED':
            self.card_machine_unreachable()

    def handle_payment_rejected(self):
        self.state.update(
            awaiting_payment_approval=False,
            rejected=True
        )
        self.timer.stop()
        AudioWorker.delayed(f"{self.curr_dir}/assets/payment_rejected.mp3")
        QTimer.singleShot(7 * 1000, lambda: self.router.pop())

    def card_machine_unreachable(self):
        AudioWorker.delayed(f"{self.curr_dir}/assets/card_machine_disconnected.mp3")
        self.timer.stop()

        if self.order_intent.productSelected == OrderProductSelected.onlyGasRefill:
            QTimer.singleShot(5 * 5000, lambda: self.card_machine_unreachable_part_2())
        else:
            QTimer.singleShot(5 * 5000, lambda: self.router.off_all("welcome"))

    def card_machine_unreachable_part_2(self):
        AudioWorker.delayed(f"{self.curr_dir}/assets/error_take_back_empty_container.mp3")

        time.sleep(5)

        GpioWorker.activate(self.order_intent.get_open_door_pin())

        time.sleep(5)
        self.router.off_all("welcome")
