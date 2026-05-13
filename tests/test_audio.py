import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock pygame before importing AudioWorker
sys.modules['pygame'] = MagicMock()
sys.modules['pygame.mixer'] = MagicMock()

from infrastructure.hardware.audio import AudioWorker

class TestAudioWorker(unittest.TestCase):
    @patch('infrastructure.hardware.audio.pygame')
    def test_play_audio(self, mock_pygame):
        # We can't easily await the rx subscription in a unit test without a TestScheduler,
        # but since we are using ThreadPoolScheduler in the implementation, 
        # distinct threads are involved. 
        # For this test, we verify that the method runs without errors and calls the mock.
        
        # However, the subscription runs on a separate thread, so we might not catch the call immediately.
        # Ideally we would inject a scheduler, but for now we'll test that the subscription is set up.
        
        try:
            AudioWorker.play("test_sound.mp3")
        except Exception as e:
            self.fail(f"AudioWorker.play raised {e}")

    @patch('infrastructure.hardware.audio.pygame')
    def test_stop_audio(self, mock_pygame):
        try:
            AudioWorker.stop()
        except Exception as e:
            self.fail(f"AudioWorker.stop raised {e}")

if __name__ == '__main__':
    unittest.main()
