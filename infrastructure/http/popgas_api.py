import requests

class PopGasApi:
    # url_base = " http://127.0.0.1:8000"
    url_base = "https://api.popgas.com.br"

    @staticmethod
    def request(method, url, **kwargs):
        try:
            modified_url = PopGasApi.url_base + url
            return requests.request(method, modified_url, **kwargs)
        except Exception as e:
            print(e)