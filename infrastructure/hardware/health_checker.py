import os

from infrastructure.http.popgas_api import PopGasApi


class HealthChecker:
    @staticmethod
    def start(app):
        print("started")
        app.after(1000 * 60, lambda: HealthChecker.ping(app))

    @staticmethod
    def ping(app):
        print("sending ping request")
        vm_id = os.environ['VENDING_MACHINE_ID']
        PopGasApi.request("PUT", f"/vending-machine-orders/{vm_id}/ping")
        app.after(1000 * 60, lambda: HealthChecker.ping(app))
