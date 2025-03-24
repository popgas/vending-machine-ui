import requests

class PopGasApi:
    url_base = "https://api.popgas.com.br"

    @staticmethod
    def request(method, url, **kwargs):
        modified_url = PopGasApi.url_base + url
        return requests.request(method, modified_url, **kwargs)