import os
import time
from datetime import datetime
from typing import Callable

import cv2
import rx
from rx.core.typing import Observer, T_in
from rx.scheduler import ThreadPoolScheduler

from infrastructure.observability.logger import Logger

class CameraResult:
    def __init__(self,  taken_photo=None, error=False):
        self.taken_photo = taken_photo
        self.error = error

class CameraWorker(Observer):
    pool_scheduler = ThreadPoolScheduler(1)

    def __init__(self, camera_socket, on_completed):
        super().__init__()
        self.camera_socket = camera_socket
        self.on_completed = on_completed
        self.result = CameraResult()
        self.logger = Logger.get_logger()

    def on_next(self, value: T_in) -> None:
        try:
            photo = self.take_photo()

            self.on_completed(CameraResult(
                taken_photo=photo,
            ))

        except Exception as e:
            self.logger.error(e)
            self.on_completed(CameraResult(
                error=True
            ))

    def on_error(self, error: Exception) -> None:
        self.logger.error(error)
        self.logger.info(error)

    def on_completed(self) -> None:
        self.logger.info(f"on_completed called {self.result}")

    @staticmethod
    def start(camera_socket, on_completed: Callable[[CameraResult], None]):
        camera = CameraWorker(camera_socket=camera_socket, on_completed=on_completed)

        rx.just(None).subscribe(camera, scheduler=CameraWorker.pool_scheduler)

    def take_photo(self):
        cap = cv2.VideoCapture(self.camera_socket)

        try:
            self.logger.info(f"using camera {self.camera_socket}")

            if not cap.isOpened():
                raise ValueError("Não foi possível abrir a câmera")

            time.sleep(1)

            # Clear buffer
            for _ in range(5):
                cap.read()

            time.sleep(1)

            ret, frame = cap.read()

            if not ret or frame is None:
                raise ValueError("Não foi possível abrir a câmera")

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Save the frame
            curr_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            cv2.imwrite(f"/tmp/photo_{curr_datetime}.jpg", gray_frame)

            return gray_frame

        except Exception as e:
            self.logger.error(f"Error in take_photo: {e}")
            raise

        finally:
            cap.release()

    @staticmethod
    def dry_run():
        cameras = [
            os.environ['CAMERA_1'],
            os.environ['CAMERA_2'],
            os.environ['CAMERA_3']
        ]
        i = 0

        for camera in cameras:
            camera = cv2.VideoCapture(camera)

            if not camera.isOpened():
                print("Error: Could not open camera.")
                exit()

            ret, frame = camera.read()
            camera.release()

            if not ret:
                print("Error: Could not read frame.")
                exit()

            cv2.imwrite(f"/tmp/photo{i}.jpg", frame)
            i = i + 1