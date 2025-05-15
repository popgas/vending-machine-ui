import time

import rx
from rx.scheduler import ThreadPoolScheduler

from domains.enums.machine_doors import VendingMachinePins
from infrastructure.observability.logger import Logger

try:
    import RPi.GPIO as GPIO
except ImportError:
    from infrastructure.hardware.dummy_gpio import DummyGPIO
    GPIO = DummyGPIO()

class GpioWorker:
    pool_scheduler = ThreadPoolScheduler(1)

    @staticmethod
    def config():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        output_pins = [
            VendingMachinePins.openDoor1,
            VendingMachinePins.openDoor2,
            VendingMachinePins.openDoor3,
            VendingMachinePins.closeDoor1,
            VendingMachinePins.closeDoor2,
            VendingMachinePins.closeDoor3,
            VendingMachinePins.rotateCarrousel,
        ]

        for pin in output_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

        GPIO.setup(VendingMachinePins.reloadDoor, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    @staticmethod
    def activate(pin):
        rx.just(pin).subscribe(
            on_next=GpioWorker.__activate_pin,
            on_completed=lambda: print("pin activated"),
            on_error=lambda e: print(f"pin not activated {e}"),
            scheduler=GpioWorker.pool_scheduler
        )

    @staticmethod
    def close_all_doors():
        GpioWorker.activate(VendingMachinePins.closeDoor1)
        GpioWorker.activate(VendingMachinePins.closeDoor2)
        GpioWorker.activate(VendingMachinePins.closeDoor3)

    @staticmethod
    def __activate_pin(pin):
        logger = Logger.get_logger()
        logger.info(f"Acionar Saida {pin}")

        try:
            GPIO.output(pin, GPIO.LOW)
            time.sleep(2)
            GPIO.output(pin, GPIO.HIGH)
        except Exception as e:
            logger.error(f"Erro ao acionar saída {pin} : {e}")
