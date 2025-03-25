import logging
import os
from datetime import datetime

class Logger:
    _logger = None

    @staticmethod
    def get_logger():
        if Logger._logger is None:
            pasta_logs = "./logs"
            os.makedirs(pasta_logs, exist_ok=True)

            nome_arquivo_log = os.path.join(pasta_logs, f"App_{datetime.now().strftime('%Y-%m-%d')}.log")

            for handler in logging.getLogger().handlers:
                handler.addFilter(FilterIgnoreStream())

            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler(nome_arquivo_log, encoding="utf-8")
                ]
            )

            Logger._logger = logging

        return Logger._logger


class FilterIgnoreStream(logging.Filter):
    def filter(self, record):
        return "STREAM" not in record.getMessage()