import requests

from infrastructure.observability.logger import Logger


class PopGasApi:
    # url_base = " http://127.0.0.1:8000"
    url_base = "https://api.popgas.com.br"

    @staticmethod
    def request(method, url, **kwargs):
        logger = Logger.get_logger()
        modified_url = PopGasApi.url_base + url

        json_body = kwargs.get('json')
        if json_body is not None:
            logger.info(f"-> {method} {modified_url} body={json_body}")
        else:
            logger.info(f"-> {method} {modified_url}")

        try:
            response = requests.request(method, modified_url, **kwargs)
            try:
                body_preview = response.text[:1000]
            except Exception:
                body_preview = "<unable to read body>"
            logger.info(f"<- {response.status_code} {modified_url} body={body_preview}")
            return response
        except Exception as e:
            logger.warning(f"!! {method} {modified_url} failed: {e}")
            return None
