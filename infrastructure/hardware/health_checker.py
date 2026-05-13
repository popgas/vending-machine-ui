from infrastructure.environment import get_env
from infrastructure.http.popgas_api import PopGasApi
from infrastructure.observability.logger import Logger


class HealthChecker:
    @staticmethod
    def start(app):
        print("started")
        app.after(1000 * 60, lambda: HealthChecker.ping(app))

    @staticmethod
    def ping(app):
        try:
            vm_id = get_env('VENDING_MACHINE_ID')
            if not vm_id:
                Logger.get_logger().warning("VENDING_MACHINE_ID ausente; ping skipped")
                return

            print("sending ping request")
            PopGasApi.request("PUT", f"/vending-machine-orders/{vm_id}/ping")
        finally:
            app.after(1000 * 60, lambda: HealthChecker.ping(app))
