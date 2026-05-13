import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock cv2
sys.modules['cv2'] = MagicMock()
import os

from infrastructure.hardware.camera import CameraWorker, CameraResult

class TestCameraWorker(unittest.TestCase):
    def test_init(self):
        worker = CameraWorker(camera_socket=0, on_completed=lambda x: None)
        self.assertIsNotNone(worker)

    @patch('infrastructure.hardware.camera.cv2')
    def test_take_photo_success(self, mock_cv2):
        # Setup mock cap
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, MagicMock()) # ret, frame
        mock_cv2.VideoCapture.return_value = mock_cap

        worker = CameraWorker(camera_socket=0, on_completed=lambda x: None)
        frame = worker.take_photo()
        self.assertIsNotNone(frame)
        mock_cap.release.assert_called()

    @patch('infrastructure.hardware.camera.cv2')
    def test_take_photo_failure(self, mock_cv2):
        # Setup mock cap to fail
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cv2.VideoCapture.return_value = mock_cap

        worker = CameraWorker(camera_socket=0, on_completed=lambda x: None)
        with self.assertRaises(ValueError):
            worker.take_photo()

    @patch('infrastructure.hardware.camera.rx')
    def test_start(self, mock_rx):
        on_completed = MagicMock()
        CameraWorker.start(0, on_completed)
        mock_rx.just.assert_called()
        
    def test_rx_methods(self):
        # Pass a mock that accepts any arguments to avoid issues with shadowed methods with different signatures
        worker = CameraWorker(0, MagicMock())
        worker.logger = MagicMock()
        
        # on_error
        worker.on_error(Exception("test"))
        worker.logger.error.assert_called()
        
        # on_completed (method) - verify the shadowed method logic
        CameraWorker.on_completed(worker)
        worker.logger.info.assert_called()
        
        # on_next success
        worker.take_photo = MagicMock(return_value="photo")
        worker.on_completed = MagicMock() # The callback property
        worker.on_next(None)
        worker.on_completed.assert_called()
        
        # on_next failure
        worker.take_photo = MagicMock(side_effect=Exception("fail"))
        worker.on_next(None)
        # Should call on_completed with error=True
        args, _ = worker.on_completed.call_args
        self.assertTrue(args[0].error)

    @patch('infrastructure.hardware.camera.cv2')
    def test_take_photo_read_fail(self, mock_cv2):
        # Scenario: isOpened True, but read fails
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        mock_cv2.VideoCapture.return_value = mock_cap
        
        worker = CameraWorker(camera_socket=0, on_completed=lambda x: None)
        with self.assertRaises(ValueError):
            worker.take_photo()

    @patch('infrastructure.hardware.camera.cv2')
    @patch.dict(os.environ, {'CAMERA_1': '0', 'CAMERA_2': '1', 'CAMERA_3': '2'})
    def test_take_photo_from_all_cameras(self, mock_cv2):
        # Mock cap
        mock_cap = MagicMock()
        mock_cv2.VideoCapture.return_value = mock_cap
        
        # Scenario 1: All success
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, MagicMock())
        mock_cv2.imencode.return_value = (True, MagicMock(tobytes=lambda: b'data'))
        
        photos = CameraWorker.take_photo_from_all_cameras()
        self.assertEqual(len(photos), 3)
        self.assertEqual(photos[0]['camera'], 1)
        
        # Scenario 2: Open fail — should skip camera and return empty list (no crash)
        mock_cap.isOpened.return_value = False
        photos = CameraWorker.take_photo_from_all_cameras()
        self.assertEqual(photos, [])
        
        # Scenario 3: Read fail
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        photos = CameraWorker.take_photo_from_all_cameras()
        self.assertEqual(photos, [])

    def asyn_wrapper(self):
        return MagicMock(__enter__=lambda *args: None, __exit__=lambda *args: None)

if __name__ == '__main__':
    unittest.main()
