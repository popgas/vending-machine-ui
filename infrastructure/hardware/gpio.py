import os
import time

import rx

from rx.scheduler import ThreadPoolScheduler

from domains.enums.machine_doors import VendingMachinePins
from infrastructure.observability.logger import Logger
from gpiozero import LED, Button

is_rp_5 = os.environ.get('RP5')
#
# try:
#     import RPi.GPIO as GPIO
# except ImportError:
#     from infrastructure.hardware.dummy_gpio import DummyGPIO
#     GPIO = DummyGPIO()

class GpioWorker:
    pool_scheduler = ThreadPoolScheduler(1)
    # reload_pin = Button(VendingMachinePins.reloadDoor, pull_up=True)
    output_pins = [
        VendingMachinePins.openDoor1,
        VendingMachinePins.openDoor2,
        VendingMachinePins.openDoor3,
        VendingMachinePins.closeDoor1,
        VendingMachinePins.closeDoor2,
        VendingMachinePins.closeDoor3,
        VendingMachinePins.rotateCarrousel,
    ]

    @staticmethod
    def config():
        """
        Configura pinos de saída e entrada de acordo com o hardware detectado.
        """
        # if is_rp_5:
        GpioWorker._config_rp_5()
        # else:
        #     GpioWorker._config_rp_3()

    @staticmethod
    def _config_rp_3():
        pass
        # # Pi 3: setup via RPi.GPIO
        # GPIO.setwarnings(False)
        # GPIO.setmode(GPIO.BCM)
        #
        # for pin in GpioWorker.output_pins:
        #     GPIO.setup(pin, GPIO.OUT)
        #     GPIO.output(pin, GPIO.HIGH)
        #
        # GPIO.setup(VendingMachinePins.reloadDoor, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    @staticmethod
    def _config_rp_5():
        # Pi 5: setup direto via libgpiod (lgpio)
        for pin_num in GpioWorker.output_pins:
            pin = LED(pin_num)
            pin.on()

    @staticmethod
    def activate(pin_num):
        rx.just(pin_num).subscribe(
            on_next=GpioWorker.__activate_pin,
            on_completed=lambda: print("Pin activated"),
            on_error=lambda e: print(f"Pin not activated: {e}"),
            scheduler=GpioWorker.pool_scheduler
        )

    @staticmethod
    def close_all_doors():
        for door_pin in (
            VendingMachinePins.closeDoor1,
            VendingMachinePins.closeDoor2,
            VendingMachinePins.closeDoor3,
        ):
            GpioWorker.activate(door_pin)

    @staticmethod
    def __activate_pin(pin_num):
        logger = Logger.get_logger()
        logger.info(f"Acionar saída {pin_num}")

        try:
            if is_rp_5:
                pin = LED(pin_num)
                pin.off()
                time.sleep(2)
                pin.on()
            else:
                pass
                # GPIO.output(pin_num, GPIO.LOW)
                # time.sleep(2)
                # GPIO.output(pin_num, GPIO.HIGH)

        except Exception as e:
            logger.error(f"Erro ao acionar saída {pin_num}: {e}")
