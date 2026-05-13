import os
import unittest
from unittest.mock import patch


class TestEnvironment(unittest.TestCase):
    def test_is_dev_mode_returns_true_on_darwin(self):
        from infrastructure.environment import is_dev_mode
        with patch('platform.system', return_value='Darwin'):
            self.assertTrue(is_dev_mode())

    def test_is_dev_mode_returns_false_on_linux(self):
        from infrastructure.environment import is_dev_mode
        with patch('platform.system', return_value='Linux'):
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


if __name__ == '__main__':
    unittest.main()
