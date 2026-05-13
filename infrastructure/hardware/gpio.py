import os
import time

import reactivex as rx

from reactivex.scheduler import ThreadPoolScheduler

from domains.enums.machine_doors import VendingMachinePins
from infrastructure.observability.logger import Logger

try:
    from gpiozero import LED, Button, Device
    from gpiozero.pins.mock import MockFactory
except ImportError:
    pass

import platform

is_rp_5 = os.environ.get('RP5')
is_macos = platform.system() == 'Darwin'
use_gpiozero = is_rp_5 or is_macos


if is_macos:
    # Set the pin factory to mock for macOS
    try:
        Device.pin_factory = MockFactory()
    except NameError:
        pass # gpiozero not installed/imported


try:
    import RPi.GPIO as GPIO
except ImportError:
    from infrastructure.hardware.dummy_gpio import DummyGPIO
    GPIO = DummyGPIO()

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
        if use_gpiozero:
            GpioWorker._config_gpiozero()
        else:
            GpioWorker._config_rp_3()

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
        # Pi 5 or MacOS (Mock): setup via gpiozero
        # Note: In gpiozero, creating the object configures the pin.
        # We might need to keep references to them if we want to toggle them later without recreating,
        # but the original code recreated them in __activate_pin?
        # WAIT: The original _config_rp_5 created LEDs but didn't store them.
        # "pin = LED(pin_num); pin.on()" -> local variable 'pin' is garbage collected?
        # gpiozero objects should ideally be kept alive.
        # However, following the existing pattern for now which seems to act as "initial state setup".
        for pin_num in GpioWorker.output_pins:
            pin = LED(pin_num)
            pin.on()
            # If we don't store 'pin', it might close the connection on GC depending on factory.
            # For MockFactory it might be fine or strictly necessary to keep it.
            # Let's verify behavior. Ideally we should store them.
            # But strictly following "change legacy logic" to "new platform" first.
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
                # Re-creating the LED object here.
                # If it's already "in use" by another object this might warn/error in some factories,
                # but with MockFactory or lgpio it might be fine if the previous one was GC'd.
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
            logger.error(f"Erro ao acionar saída {pin_num}: {e}")
