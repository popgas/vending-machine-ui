import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock hardware libraries
sys.modules['RPi'] = MagicMock()
sys.modules['RPi.GPIO'] = MagicMock()
sys.modules['gpiozero'] = MagicMock()

from infrastructure.hardware.gpio import GpioWorker, VendingMachinePins

class TestGpioWorker(unittest.TestCase):
    @patch('infrastructure.hardware.gpio.GPIO')
    def test_config_rp3(self, mock_gpio):
        with patch('infrastructure.hardware.gpio.is_rp_5', False):
            with patch('infrastructure.hardware.gpio.is_macos', False):
                with patch('infrastructure.hardware.gpio.use_gpiozero', False):
                    GpioWorker.config()
                    mock_gpio.setmode.assert_called_with(mock_gpio.BCM)
                    mock_gpio.setup.assert_called()

    @patch('infrastructure.hardware.gpio.LED')
    def test_config_rp5(self, mock_led):
        with patch('infrastructure.hardware.gpio.is_rp_5', True):
            GpioWorker.config()
            mock_led.assert_called()
            mock_led.return_value.on.assert_called()

    @patch('infrastructure.hardware.gpio.rx')
    def test_activate_pin_subscription(self, mock_rx):
        GpioWorker.activate(1)
        mock_rx.just.assert_called_with(1)
        
    def test_activate_pin_rp3_logic(self):
        with patch('infrastructure.hardware.gpio.GPIO') as mock_gpio:
            with patch('infrastructure.hardware.gpio.is_rp_5', False):
                # Access private method via name mangling or just call activate (which uses rx)
                # To call the logic directly without rx async/thread issues:
                GpioWorker._config_rp_3() # Ensure config doesn't error
                
                # We can call the callback directly to test the logic
                GpioWorker._GpioWorker__activate_pin(12)
                
                mock_gpio.output.assert_called()
                
    def test_activate_pin_rp5_logic(self):
         with patch('infrastructure.hardware.gpio.LED') as mock_led:
            with patch('infrastructure.hardware.gpio.is_rp_5', True):
                GpioWorker._GpioWorker__activate_pin(12)
                mock_led.assert_called_with(12)
                mock_led.return_value.off.assert_called()
                
    def test_activate_pin_error(self):
        # Force an error
        with patch('infrastructure.hardware.gpio.Logger') as mock_logger:
            with patch('infrastructure.hardware.gpio.GPIO') as mock_gpio:
                mock_gpio.output.side_effect = Exception("error")
                with patch('infrastructure.hardware.gpio.is_rp_5', False):
                    with patch('infrastructure.hardware.gpio.is_macos', False):
                        with patch('infrastructure.hardware.gpio.use_gpiozero', False):
                            GpioWorker._GpioWorker__activate_pin(12)
                            mock_logger.get_logger.return_value.warning.assert_called()

    def test_close_all_doors(self):
         with patch.object(GpioWorker, 'activate') as mock_activate:
             GpioWorker.close_all_doors()
             self.assertEqual(mock_activate.call_count, 3)

if __name__ == '__main__':
    unittest.main()
