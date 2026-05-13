import os
import unittest
from unittest.mock import patch


class TestEnvironment(unittest.TestCase):
    def test_is_dev_mode_returns_true_on_darwin(self):
        from infrastructure.environment import is_dev_mode
        with patch('infrastructure.environment.platform.system', return_value='Darwin'):
            self.assertTrue(is_dev_mode())

    def test_is_dev_mode_returns_false_on_linux(self):
        from infrastructure.environment import is_dev_mode
        with patch('infrastructure.environment.platform.system', return_value='Linux'):
            self.assertFalse(is_dev_mode())

    def test_get_env_returns_value_when_set(self):
        from infrastructure.environment import get_env
        with patch.dict(os.environ, {'FOO': 'bar'}):
            self.assertEqual(get_env('FOO'), 'bar')

    def test_get_env_returns_default_when_missing(self):
        from infrastructure.environment import get_env
        # garantir que a var não exista
        os.environ.pop('MISSING_KEY', None)
        self.assertEqual(get_env('MISSING_KEY', 'fallback'), 'fallback')

    def test_get_env_returns_none_when_missing_no_default(self):
        from infrastructure.environment import get_env
        os.environ.pop('MISSING_KEY', None)
        self.assertIsNone(get_env('MISSING_KEY'))

    def test_get_env_logs_warning_when_missing_in_production(self):
        from infrastructure.environment import get_env
        os.environ.pop('MISSING_KEY', None)
        with patch('infrastructure.environment.is_dev_mode', return_value=False):
            with patch('infrastructure.environment.Logger') as mock_logger:
                get_env('MISSING_KEY')
                mock_logger.get_logger.return_value.warning.assert_called_once()

    def test_get_env_does_not_log_warning_in_dev_mode(self):
        from infrastructure.environment import get_env
        os.environ.pop('MISSING_KEY', None)
        with patch('infrastructure.environment.is_dev_mode', return_value=True):
            with patch('infrastructure.environment.Logger') as mock_logger:
                get_env('MISSING_KEY')
                mock_logger.get_logger.return_value.warning.assert_not_called()

    def test_get_env_logs_warning_even_when_default_provided_in_production(self):
        """The key bug: warning must fire even when default is provided."""
        from infrastructure.environment import get_env
        os.environ.pop('MISSING_KEY', None)
        with patch('infrastructure.environment.is_dev_mode', return_value=False):
            with patch('infrastructure.environment.Logger') as mock_logger:
                result = get_env('MISSING_KEY', 'fallback')
                self.assertEqual(result, 'fallback')
                mock_logger.get_logger.return_value.warning.assert_called_once()


if __name__ == '__main__':
    unittest.main()
