import tkinter as tk

from domains.enums.order_product_selected import OrderProductSelected
from infrastructure.hardware.audio import AudioWorker
from infrastructure.hardware.gpio import GpioWorker
from presentation.abstractions.new_order_intent import NewOrderIntent
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.enums.alignment import Side, Anchor, Fill
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets, CircularSpinner
from presentation.views.components.layout.padding import Padding
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerVertical, SpacerHorizontal
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.state_provider import StateProvider
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from application import Application
from presentation.views.screens.payment_selection.payment_selection_state import PaymentSelectionState
from utils.file import FileUtils
from utils.formatter import Formatter


class PaymentSelectionScreen(tk.Frame):
    def __init__(self, app: Application, order_intent: NewOrderIntent):
        super().__init__(app.container, bg="#FFFFFF")
        self.order_intent = order_intent
        self.app = app
        self.curr_dir = FileUtils.dir(__file__)
        self.state = PaymentSelectionState()
        self.clicked = False

        can_pop = order_intent.productSelected == OrderProductSelected.gasWithContainer

        StateProvider(
            parent=self,
            state=self.state,
            child=lambda: Column(
                expand=True,
                children=[
                    TransparentTopBar(app, can_pop=can_pop),
                    self.body_content()
                ]
            )
        )

        AudioWorker.play(f"{self.curr_dir}/assets/audio.mp3")

    def body_content(self) -> BuildableWidget:
        if self.state.cancelling is False:
            return self.payment_buttons()
        else:
            return self.canceling_view()

    def canceling_view(self):
        return Column(
            expand=True,
            children=[
                SpacerVertical(),
                CircularSpinner(root=self.app, side=Side.TOP, anchor=Anchor.CENTER),
                SizedBox(height=20),
                Text("Cancelando operação",
                     font_size=27,
                     color="darkred"),
                SizedBox(height=30),
                Text("Iremos abrir a porta novamente para que você retire seu botijão vazio.",
                     font_size=16,
                     color="#333"),
                SizedBox(height=10),
                Text("A porta ficará aberta por 15 segundos e depois irá fechar.",
                     font_size=16,
                     color="#333"),
                SizedBox(height=10),
                Text("Por favor, afaste-se.",
                     font_size=16,
                     color="#333"),
                SpacerVertical(),
            ]
        )

    def get_price_for_payment_method(self, payment_method_id: int) -> float:
        prices = self.order_intent.pricesByPaymentMethod[str(payment_method_id)]

        if self.order_intent.productSelected == OrderProductSelected.gasWithContainer:
            return float(prices['gas_price'] + prices['container_price'])
        else:
            return float(prices['gas_price'])

    def payment_buttons(self) -> BuildableWidget:
        return Column(
            expand=True,
            children=[
                SpacerVertical(),
                Text("Selecione", font_size=40, color=ColorPalette.blue3),
                Text("a forma de pagamento", font_size=40, color=ColorPalette.blue3),
                SizedBox(height=60),
                Column(
                    expand=True,
                    children=[
                        self.payment_button(
                            image=ImageFromAssets(
                                path=f"{self.curr_dir}/assets/cartao.png",
                                width=58,
                                height=57,
                            ),
                            title="Cartão de Débito",
                            price=self.get_price_for_payment_method(2),
                            onclick=lambda: self.debit_card()
                        ),
                        self.payment_button(
                            image=ImageFromAssets(
                                path=f"{self.curr_dir}/assets/cartao.png",
                                width=58,
                                height=57,
                            ),
                            title="Cartão de Crédito",
                            price=self.get_price_for_payment_method(3),
                            onclick=lambda: self.credit_card()
                        ),
                        self.payment_button(
                            image=ImageFromAssets(
                                path=f"{self.curr_dir}/assets/pix.png",
                                width=58,
                                height=57,
                            ),
                            title="PIX",
                            price=self.get_price_for_payment_method(5),
                            onclick=lambda: self.pix_machine()
                        ),
                        Row(
                            expand=True,
                            side=Side.TOP,
                            fill=Fill.NONE,
                            children=[
                                Row(
                                    width=int(self.app.container.winfo_width() * 0.8),
                                    height=150,
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
                                )
                            ]
                        )
                    ],
                ),
                SpacerVertical(),
            ],
        )

    def cancel_operation(self):
        if self.order_intent.productSelected == OrderProductSelected.gasWithContainer:
            self.app.off_all("welcome")
        elif self.order_intent.productSelected == OrderProductSelected.onlyGasRefill:
            self.state.update(cancelling=True)
            AudioWorker.play(f"{self.curr_dir}/assets/payment_cancellation.mp3")
            GpioWorker.activate(self.order_intent.get_refill_open_door_pin())
            self.app.after(20 * 1000, lambda: AudioWorker.play(f"{self.curr_dir}/assets/door_will_close_now.mp3"))
            self.app.after(23 * 1000, lambda: GpioWorker.close_all_doors())
            self.app.after(30 * 1000, lambda: self.app.off_all("welcome"))

    def payment_button(self, image, title, onclick, price: float) -> BuildableWidget:
        return Row(
            expand=True,
            side=Side.TOP,
            fill=Fill.NONE,
            children=[
                Row(
                    width=int(self.app.container.winfo_width() * 0.8),
                    height=120,
                    children=[
                        Column(
                            side=Side.LEFT,
                            anchor=Anchor.CENTER,
                            children=[
                                SizedBox(width=30),
                                image,
                                SizedBox(width=20),
                                Text(title,
                                     font_size=24,
                                     side=Side.LEFT,
                                     anchor=Anchor.RIGHT,
                                     color="#fff"
                                     ),
                            ]
                        ),
                        SpacerHorizontal(),
                        Column(
                            side=Side.TOP,
                            anchor=Anchor.TOP,
                            expand=True,
                            children=[
                                Text(Formatter.currency(price),
                                 color="#fff",
                                 side=Side.TOP,
                                 anchor=Anchor.RIGHT,
                                 padding=Padding(right=15),
                                 font_size=30,
                                 ),
                            ]
                        ),
                    ],
                    background_color=ColorPalette.blue3,
                    border_radius=8,
                    fill=Fill.X,
                    border_color="#ccc",
                    on_click=onclick,
                )
            ]
        )

    def on_route_popped(self):
        self.clicked = False

    def debit_card(self):
        if self.clicked is True:
            return

        self.clicked = True

        AudioWorker.stop()
        self.app.push('card_machine', self.order_intent.copy_with(
            paymentMethodId=2,
            selectedPaymentMethodPrice=self.get_price_for_payment_method(2)
        ))

    def credit_card(self):
        if self.clicked is True:
            return

        self.clicked = True

        AudioWorker.stop()
        self.app.push('card_machine', self.order_intent.copy_with(
            paymentMethodId=3,
            selectedPaymentMethodPrice=self.get_price_for_payment_method(3)
        ))

    def pix_machine(self):
        if self.clicked is True:
            return

        self.clicked = True

        AudioWorker.stop()
        self.app.push('card_machine', self.order_intent.copy_with(
            paymentMethodId=5,
            selectedPaymentMethodPrice=self.get_price_for_payment_method(5)
        ))
