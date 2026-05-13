import os
import time

import reactivex as rx

from reactivex.scheduler import ThreadPoolScheduler

from domains.enums.machine_doors import VendingMachinePins
from infrastructure.environment import is_dev_mode
from infrastructure.observability.logger import Logger

try:
    from gpiozero import LED, Button, Device
    from gpiozero.pins.mock import MockFactory
except ImportError:
    pass

is_rp_5 = os.environ.get('RP5')
is_macos = is_dev_mode()
use_gpiozero = is_rp_5 or is_macos


if is_macos:
    # Set the pin factory to mock for macOS
    try:
        Device.pin_factory = MockFactory()
    except NameError:
        pass  # gpiozero not installed/imported


try:
    import RPi.GPIO as GPIO
except ImportError:
    from infrastructure.hardware.dummy_gpio import DummyGPIO
    GPIO = DummyGPIO()


class GpioWorker:
    pool_scheduler = ThreadPoolScheduler(1)
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
        """Configura pinos de saída e entrada de acordo com o hardware detectado."""
        try:
            if use_gpiozero:
                GpioWorker._config_gpiozero()
            else:
                GpioWorker._config_rp_3()
        except Exception as e:
            Logger.get_logger().warning(f"GPIO config skipped: {e}")

    @staticmethod
    def _config_rp_3():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        for pin in GpioWorker.output_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

        GPIO.setup(VendingMachinePins.reloadDoor, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    @staticmethod
    def _config_gpiozero():
        for pin_num in GpioWorker.output_pins:
            pin = LED(pin_num)
            pin.on()
            pin.close()

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
            if use_gpiozero:
                pin = LED(pin_num)
                pin.off()
                time.sleep(2)
                pin.on()
                pin.close()
            else:
                GPIO.output(pin_num, GPIO.LOW)
                time.sleep(2)
                GPIO.output(pin_num, GPIO.HIGH)

        except Exception as e:
            logger.warning(f"GPIO activate skipped on pin {pin_num}: {e}")
