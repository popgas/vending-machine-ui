from infrastructure.hardware.gpio import GpioWorker
from presentation.views.screens.camera_verification.camera_verification import CameraVerificationScreen
from presentation.views.screens.card_machine.card_machine import CardMachineScreen
from presentation.views.screens.emtpy_stock.empty_stock import EmptyStockScreen
from presentation.views.screens.order_completed.order_completed import OrderCompletedScreen
from presentation.views.screens.payment_selection.payment_selection import PaymentSelectionScreen
from presentation.views.screens.place_empty_container.place_empty_container import PlaceEmptyContainerScreen
from presentation.views.screens.preparing_order.preparing_order import PreparingOrderScreen
from presentation.views.screens.product_selected.product_selected import ProductSelectionScreen
from presentation.views.screens.technical_support.technical_support import TechSupportScreen
from presentation.views.screens.welcome.welcome import WelcomeScreen
from application import Application
import tkinter as tk

# def start_loop(loop):
#     asyncio.set_event_loop(loop)
#     loop.run_forever()

if __name__ == '__main__':
    GpioWorker.config()

    # bg_loop = asyncio.new_event_loop()
    # thread = threading.Thread(target=start_loop, args=(bg_loop,), daemon=True)
    # thread.start()
    # asyncio.run_coroutine_threadsafe(Websocket.configure(), bg_loop)

    app = Application({
        'welcome': lambda *args: WelcomeScreen(*args),
        'product_selection': lambda *args: ProductSelectionScreen(*args),
        'place_empty_container': lambda *args: PlaceEmptyContainerScreen(*args),
        'payment_selection': lambda *args: PaymentSelectionScreen(*args),
        'camera_verification': lambda *args: CameraVerificationScreen(*args),
        'preparing_order': lambda *args: PreparingOrderScreen(*args),
        'card_machine': lambda *args: CardMachineScreen(*args),
        'order_completed': lambda *args: OrderCompletedScreen(*args),
        'empty_stock': lambda *args: EmptyStockScreen(*args),
        'tech_support': lambda *args: TechSupportScreen(*args),
    })
    photo = tk.PhotoImage(file='assets/icons/application_icon.png')
    app.wm_iconphoto(False, photo)

    app.attributes("-fullscreen", True)
    # app.push("card_machine", NewOrderIntent(
    #     productSelected=OrderProductSelected.onlyGasRefill,
    #     productPrice=100,
    #     stockCount=40,
    #     paymentMethodId=5,
    #     correlationId="1234"
    # ))
    app.push("welcome")
    app.mainloop()