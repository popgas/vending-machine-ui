import unittest
from unittest.mock import MagicMock

# Reaproveita os mocks de hardware/Tk do teste de integração (aplicados no import).
from tests import test_integration  # noqa: F401
from infrastructure.http.popgas_api import requests as api_requests
from presentation.abstractions.new_order_intent import NewOrderIntent
from domains.enums.order_product_selected import OrderProductSelected
from presentation.views.screens.card_machine import card_machine
from presentation.views.screens.card_machine.card_machine import CardMachineScreen


def response(body):
    r = MagicMock()
    r.json.return_value = body
    r.text = str(body)
    r.status_code = 200
    return r


class TestCardMachineTimeout(unittest.TestCase):
    def setUp(self):
        self.app = MagicMock()
        self.app.container.winfo_width.return_value = 800
        self.scheduled = []
        self.app.after.side_effect = lambda ms, func=None: self.scheduled.append((ms, func)) or f"t{len(self.scheduled)}"
        self.request = api_requests.request
        self.request.reset_mock()
        self.request.side_effect = None

    def screen(self, payment_method_id=2):
        intent = NewOrderIntent(
            productSelected=OrderProductSelected.onlyGasRefill,
            productPrice=99.9,
            stockCount=1,
            paymentMethodId=payment_method_id,
            selectedPaymentMethodPrice=99.9,
        )
        screen = CardMachineScreen(self.app, intent)
        self.request.side_effect = [
            response({"id": 10, "correlation_id": "corr-1", "pix_qr_code": None}),
            response({"payment_status": "PENDING", "flow_status": "PENDING"}),
        ]
        screen.create_order_request()
        self.request.side_effect = None
        return screen

    def delays(self):
        return [ms for ms, _ in self.scheduled]

    def test_card_payment_asks_to_remove_the_card_at_5_and_7_minutes(self):
        screen = self.screen()

        self.assertIn(5 * 60 * 1000, self.delays())
        self.assertIn(7 * 60 * 1000, self.delays())
        self.assertIn(card_machine.PAYMENT_TIMEOUT_MS, self.delays())

        screen.show_remove_card_prompt()
        self.assertTrue(screen.state.remove_card_prompt)
        self.assertTrue(screen.state.awaiting_payment_approval)

    def test_pix_on_screen_does_not_ask_to_remove_the_card(self):
        self.screen(payment_method_id=5)

        self.assertNotIn(5 * 60 * 1000, self.delays())
        self.assertNotIn(7 * 60 * 1000, self.delays())

    def test_timeout_tells_the_api_and_releases_the_gas_if_it_was_just_approved(self):
        screen = self.screen()
        self.request.return_value = response({"payment_status": "APPROVED", "flow_status": "COMPLETED"})

        screen.handle_payment_timeout()

        method, url = self.request.call_args[0][:2]
        self.assertEqual(method, 'POST')
        self.assertTrue(url.endswith('/vending-machine-orders/corr-1/abandon'))
        self.app.push.assert_called_once()
        self.assertEqual(self.app.push.call_args[0][0], 'preparing_order')
        self.assertFalse(screen.state.rejected)

    def test_timeout_without_approval_shows_time_is_up(self):
        screen = self.screen()
        self.request.return_value = response({"payment_status": "PENDING", "flow_status": "PENDING"})

        screen.handle_payment_timeout()

        self.app.push.assert_not_called()
        self.assertTrue(screen.state.rejected)
        self.assertTrue(screen.state.timed_out)
        self.assertFalse(screen.state.awaiting_payment_approval)

    def test_timeout_when_the_api_is_unreachable_still_gives_up(self):
        screen = self.screen()
        self.request.side_effect = Exception("sem rede")

        screen.handle_payment_timeout()

        self.app.push.assert_not_called()
        self.assertTrue(screen.state.rejected)

    def test_prompt_is_ignored_after_the_payment_finished(self):
        screen = self.screen()
        screen.state.update(awaiting_payment_approval=False)

        screen.show_remove_card_prompt()

        self.assertFalse(screen.state.remove_card_prompt)


if __name__ == '__main__':
    unittest.main()
