import time

from infrastructure.observability.logger import Logger

try:
    import RPi.GPIO as GPIO
except ImportError:
    from unittest.mock import MagicMock as GPIO

class GpioWorker:
    @staticmethod
    def activate(pin):
        logger = Logger.get_logger()
        logger.info(f"Acionar Saida {pin}")

        try:
            GPIO.output(pin, GPIO.LOW)
            time.sleep(2)
            GPIO.output(pin, GPIO.HIGH)
        except Exception as e:
            logger.error(f"Erro ao acionar saída {pin} : {e}")