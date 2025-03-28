import time

import rx
from rx.scheduler import ThreadPoolScheduler

from infrastructure.observability.logger import Logger

try:
    import RPi.GPIO as GPIO
except ImportError:
    from unittest.mock import MagicMock as GPIO

class GpioWorker:
    pool_scheduler = ThreadPoolScheduler(1)

    @staticmethod
    def activate(pin):
        rx.just(pin).subscribe(
            on_next=GpioWorker.__activate_pin,
            on_completed=lambda: print("pin activated"),
            on_error=lambda: print("pin not activated"),
            scheduler=GpioWorker.pool_scheduler
        )

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