import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json

# --- 1. MOCK HARDWARE & GUI DEPENDENCIES ---
# We must mock these BEFORE importing any module that uses them.

# Mock Tkinter
mock_tk = MagicMock()


class MockWidget:
    def __init__(self, master=None, *args, **kwargs):
        pass

    def __getitem__(self, key):
        return MagicMock()

    def __setitem__(self, key, value):
        pass
        
    def __getattr__(self, name):
        return MagicMock()
        
    def __call__(self, *args, **kwargs):
        return MagicMock()

class MockVar:
    def __init__(self, *args, **kwargs):
        pass
    def set(self, value): pass
    def get(self): return ""

mock_tk.Frame = MockWidget
mock_tk.Tk = MockWidget
mock_tk.StringVar = MockVar
mock_tk.IntVar = MockVar
mock_tk.BooleanVar = MockVar
mock_tk.DoubleVar = MockVar
mock_tk.PhotoImage = MockWidget # PhotoImage is widget-like enough

sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.font'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()

# Mock Pygame
mock_pygame = MagicMock()
sys.modules['pygame'] = mock_pygame
sys.modules['pygame.mixer'] = MagicMock()

# Mock CV2
mock_cv2 = MagicMock()
sys.modules['cv2'] = mock_cv2

# Mock GPIO
sys.modules['RPi'] = MagicMock()
sys.modules['RPi.GPIO'] = MagicMock()
sys.modules['gpiozero'] = MagicMock()

# Mock Ably
sys.modules['ably'] = MagicMock()

# Mock Requests (since it's missing in env)
sys.modules['requests'] = MagicMock()

# Mock qrcode
sys.modules['qrcode'] = MagicMock()

# Mock PIL
mock_pil = MagicMock()
mock_pil.ImageSequence.Iterator.return_value = [MagicMock()] # Return one frame
sys.modules['PIL'] = mock_pil
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['PIL.ImageSequence'] = mock_pil.ImageSequence

# --- 2. SET ENVIRONMENT VARIABLES ---
os.environ['VENDING_MACHINE_ID'] = 'vm-test-01'
os.environ['CAMERA_1'] = '0'
os.environ['CAMERA_2'] = '1'
os.environ['CAMERA_3'] = '2'


# --- 3. IMPORT MODULES UNDER TEST ---
# Now we can safely import the application modules
from application import Application
from presentation.views.screens.product_selected.product_selected import ProductSelectionScreen
from presentation.views.screens.camera_verification.camera_verification import CameraVerificationScreen
from presentation.views.screens.card_machine.card_machine import CardMachineScreen
from presentation.abstractions.new_order_intent import NewOrderIntent
from domains.enums.order_product_selected import OrderProductSelected
from infrastructure.http.popgas_api import PopGasApi
from infrastructure.hardware.camera import CameraResult

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Setup Mock App
        self.mock_app = MagicMock()
        self.mock_app.container = MagicMock()
        # Mockingwinfo_width to return a valid int for layout calculations
        self.mock_app.container.winfo_width.return_value = 800 
        
        def custom_after(ms, func=None):
            if func:
                # Avoid recursion for animation loops by checking method name
                # 'animate' is used in CircularSpinner
                if hasattr(func, '__name__') and func.__name__ == 'animate':
                    return "timer_id"
                
                # Check for long timeouts (e.g. > 10s) and ignore them
                # 300*1000 = 300000ms
                if ms > 10000:
                    return "timeout_id"

                # Otherwise, execute immediately
                func()
            return "timer_id"

        self.mock_app.after.side_effect = custom_after 
        
        # Mock requests
        from infrastructure.http.popgas_api import requests as api_requests
        self.mock_request = api_requests.request
        self.mock_request.reset_mock()
        

    def tearDown(self):
        pass

    def test_full_order_flow(self):
        """
        Simulates:
        ...
        """
        
        # --- STEP 1: PRODUCT SELECTION ---
        print("\n--- Testing Product Selection Screen ---")
        
        # Mock API response for prices
        self.mock_request.return_value.json.return_value = {
            "gas_refill_price": "100.0",
            "container_price": "50.0",
            "container_full_stock_count": "10",
            "prices_by_payment_method": {"credit": 150.0},
            "is_under_maintenance": False
        }

        # Initialize Screen
        screen = ProductSelectionScreen(self.mock_app)
        
        # Verify API called
        self.mock_request.assert_called_with(
            "GET", 
            "https://api.popgas.com.br/vending-machine-orders/vm-test-01/prices"
        )
        
        # Simulate user clicking "Gas + Container"
        # We access the method directly to simulate the click action
        screen.go_to_payment_selection_screen()
        
        # Verify navigation to 'payment_selection'
        self.mock_app.push.assert_called()
        args, _ = self.mock_app.push.call_args
        self.assertEqual(args[0], 'payment_selection')
        intent: NewOrderIntent = args[1]
        self.assertEqual(intent.productSelected, OrderProductSelected.gasWithContainer)
        self.assertEqual(intent.productPrice, 150.0)

        print("Product Selection: OK")


        # --- STEP 2: CAMERA VERIFICATION ---
        print("\n--- Testing Camera Verification Screen ---")
        # Reuse intent from previous step, assuming user selected refill for camera flow (just to test camera logic)
        # Actually camera verification happens for Refill only typically, but let's test the screen logic itself.
        
        # Mock API response for verification
        self.mock_request.return_value.json.return_value = {
            "passed_verification": True
        }
        
        # Mock Camera Worker to return success immediately
        # We need to patch CameraWorker.start because it's called in __init__ via verify_placed_container
        with patch('infrastructure.hardware.camera.CameraWorker.start') as mock_camera_start:
             # Initialize Screen
             camera_screen = CameraVerificationScreen(self.mock_app, intent)
             
             # Simulate CameraWorker completing successfully
             # The screen calls verify_placed_container -> CameraWorker.start
             # We simulate the callback execution
             callback = mock_camera_start.call_args[1]['on_completed']
             
             # Create a dummy photo
             dummy_photo = MagicMock() 
             result = CameraResult(taken_photo=dummy_photo)
             
             # Trigger callback
             # We also need to mock cv2.imencode inside handle_camera_callback
             # mock_cv2 is already globally mocked at top
             mock_buffer = MagicMock()
             mock_buffer.tobytes.return_value = b'fake_jpg_bytes'
             mock_cv2.imencode.return_value = (True, mock_buffer)
             
             camera_screen.handle_camera_callback(result, try_again=True)

             # Verify API called
             # The URL should match verify-photo
             call_args = self.mock_request.call_args
             self.assertEqual(call_args[0][0], "POST")
             self.assertIn("/verify-photo", call_args[0][1])
             
             # Verify navigation to payment_selection again (success path)
             expect_intent = intent.copy_with(placedContainerPhoto=dummy_photo)
             self.mock_app.push.assert_called_with("payment_selection", expect_intent)
        
        print("Camera Verification: OK")


        # --- STEP 3: CARD MACHINE (PAYMENT) ---
        print("\n--- Testing Card Machine Screen ---")
        
        # Mock Create Order Response
        self.mock_request.return_value.json.side_effect = [
            # 1. POST /vending-machine-orders (Create)
            {
                "id": "order_123",
                "correlation_id": "corr_ABC",
                "pix_qr_code": "pix_code_123"
            },
            # 2. GET /vending-machine-orders/corr_ABC (Poll 1 - Approved)
            {
                "payment_status": "APPROVED",
                "flow_status": "NORMAL"
            }
        ]

        # Initialize Screen - triggers create_order_request in after(200)
        # Initialize Screen - triggers create_order_request in after(200)
        # We mock app.after to run immediately or manually trigger
        # We rely on custom_after from setUp which runs immediate short timers.
        pass
        
        # We need to ensure state provider doesn't crash
        # It uses the passed child lambda.
        
        card_screen = CardMachineScreen(self.mock_app, intent)
        
        # Manually trigger the delayed creation if after Mock didn't catch it correctly or if we crave explicit control
        # With the side_effect above, it executes immediately inside __init__
        
        # Check if POST was called
        # self.mock_request.assert_any_call("POST", ...) logic is complex with side_effect
        # Let's inspect call history
        
        # Expected calls:
        # 1. Product Selection GET
        # 2. Camera Verification POST
        # 3. Card Machine POST (Create)
        # 4. Card Machine GET (Poll)
        
        # Let's filter for POST /vending-machine-orders
        post_calls = [c for c in self.mock_request.mock_calls if "POST" in str(c) and "/vending-machine-orders" in str(c) and "verify" not in str(c)]
        self.assertTrue(len(post_calls) > 0, "Order creation API not called")
        
        # Check if polling happened
        # card_screen.check_order_payment_status() should have been called
        
        # Verify navigation to 'preparing_order'
        # The logic calls app.push('preparing_order', ...) on APPROVED
        
        self.mock_app.push.assert_called()
        last_call_args = self.mock_app.push.call_args
        self.assertEqual(last_call_args[0][0], 'preparing_order')
        
        print("Card Machine: OK")
        print("\n--- Integration Test Passed ---")


if __name__ == '__main__':
    unittest.main()
