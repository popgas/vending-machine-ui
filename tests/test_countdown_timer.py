import unittest
from unittest.mock import MagicMock, call
import sys

# Mock Tkinter dependencies
mock_tk = MagicMock()
class MockVar:
    def __init__(self, value=None):
        self._val = value
    def set(self, value):
        self._val = value
    def get(self):
        return self._val

mock_tk.StringVar = MockVar
sys.modules['tkinter'] = mock_tk

from presentation.views.components.state.countdown_timer import CountdownTimer

class TestCountdownTimer(unittest.TestCase):
    def setUp(self):
        self.mock_app = MagicMock()
        # Mock 'after' to capture callback
        self.mock_app.after = MagicMock()
        self.mock_app.after_cancel = MagicMock()
        
    def test_initialization(self):
        timer = CountdownTimer(
            initial_value=10, 
            text_builder=lambda x: str(x), 
            on_reached_zero=MagicMock(), 
            app=self.mock_app, 
            autostart=False
        )
        self.assertEqual(timer.initial_value, 10)
        self.assertIsInstance(timer.text, MockVar)
        self.assertEqual(timer.text.get(), "10")

    def test_start_and_tick(self):
        on_reached_zero = MagicMock()
        text_builder = lambda x: str(x)
        
        timer = CountdownTimer(
            initial_value=2, 
            text_builder=text_builder, 
            on_reached_zero=on_reached_zero, 
            app=self.mock_app,
            autostart=False
        )
        
        # Timer needs a widget to count down, or it waits
        timer.widget = MagicMock()
        timer.widget.winfo_exists.return_value = True

        timer.start()
        
        # Verify initial callback scheduled
        self.mock_app.after.assert_called_with(1000, timer.countdown)
        
        # Manually trigger countdown tick (2 -> 1)
        timer.countdown()
        self.assertEqual(timer.current_value, 1)
        self.assertEqual(timer.text.get(), "1")
        
        # Callback check - Should NOT be called yet (checked at start of NEXT tick)
        on_reached_zero.assert_not_called()
        
        # Manually trigger countdown tick (1 -> check -> callback)
        timer.countdown()
        # Should return early because current_value is 1 at start of method
        self.assertTrue(timer.has_reached_zero)
        on_reached_zero.assert_called_once()

    def test_stop(self):
        timer = CountdownTimer(
            initial_value=10, 
            text_builder=lambda x: str(x), 
            on_reached_zero=MagicMock(), 
            app=self.mock_app
        )
        timer.cancel()
        self.mock_app.after_cancel.assert_called()
        self.assertTrue(timer.has_reached_zero)
        self.assertEqual(timer.current_value, 0)

if __name__ == '__main__':
    unittest.main()
