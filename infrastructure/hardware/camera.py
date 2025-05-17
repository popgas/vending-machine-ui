import glob
import os
import time
from datetime import datetime
from typing import Callable

import cv2
import numpy as np
import rx
from rx.core.typing import Observer, T_in
from rx.scheduler import ThreadPoolScheduler

from infrastructure.observability.logger import Logger

class CameraResult:
    def __init__(self, best_score_security=0, best_score_empty=0, best_score_image=None, taken_photo=None, error=False):
        self.best_score_security = best_score_security
        self.best_score_empty = best_score_empty
        self.best_score_image = best_score_image
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
            security_images = self.load_security_images("./assets/images/security-camera-images/*.png")
            empty_images = self.load_security_images("./assets/images/empty-camera-images/*.jpg")
            photo = self.take_photo()

            self.result = self.is_eligible(photo, security_images, empty_images)
            self.on_completed(self.result)

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

    def is_eligible(self, photo, security_images, empty_images) -> CameraResult:
        result = CameraResult(
            best_score_security=0,
            best_score_empty=0,
            best_score_image=None,
            taken_photo=None
        )

        for idx, fixed_image in enumerate(security_images):
            score = self.compare_images(photo, fixed_image['content'])

            self.logger.info(f"score: {score}, img: {fixed_image['path']}")

            if score > result.best_score_security:
                result = CameraResult(
                    best_score_security=score,
                    best_score_image=fixed_image['content'],
                    taken_photo=photo
                )

        for idx, fixed_image in enumerate(empty_images):
            score = self.compare_images(photo, fixed_image['content'])

            self.logger.info(f"score: {score}, img: {fixed_image['path']}")

            if score > result.best_score_empty:
                result = CameraResult(
                    best_score_security=result.best_score_security,
                    best_score_empty=score,
                    best_score_image=result.best_score_image,
                    taken_photo=result.taken_photo
                )

        self.logger.info(f"nota comparação botijão: {result.best_score_security}")
        self.logger.info(f"nota comparação vazio: {result.best_score_empty}")

        return result

    def to_gray(self, image):
        # Check if the image is already grayscale
        if len(image.shape) == 2 or image.shape[2] == 1:
            return image
        else:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def compare_images(self, photo, fixed_image):
        resized_frame = cv2.resize(photo, (fixed_image.shape[1], fixed_image.shape[0]))
        correlation = cv2.matchTemplate(resized_frame, fixed_image, cv2.TM_CCOEFF_NORMED)
        max_corr = np.max(correlation)

        return max_corr

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

    def load_security_images(self, path):
        fixed_image_paths = glob.glob(path)
        images = []

        for image in fixed_image_paths:
            loaded = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
            if loaded is not None:
                images.append({
                    'content': loaded,
                    'path': image
                })
                self.logger.info(f"Imagem carregada: {image}")
            else:
                self.logger.error(f"Erro ao carregar a imagem: {image}")

        if not images:
            self.logger.warning("Nenhuma imagem válida foi encontrada na pasta.")

        return images

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