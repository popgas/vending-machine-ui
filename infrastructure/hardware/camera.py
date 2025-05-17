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
    def __init__(self, best_score=0, best_score_image=None, taken_photo=None, error=False):
        self.best_score = best_score
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
            security_images = self.load_security_images()
            photo = self.take_photo()

            self.result = self.is_eligible(photo, security_images)
            self.on_completed(self.result)

        except Exception as e:
            self.on_completed(CameraResult(
                error=True
            ))

    def on_error(self, error: Exception) -> None:
        self.logger.info(error)

    def on_completed(self) -> None:
        self.logger.info(f"on_completed called {self.result}")

    @staticmethod
    def start(camera_socket, on_completed: Callable[[CameraResult], None]):
        camera = CameraWorker(camera_socket=camera_socket, on_completed=on_completed)

        rx.just(None).subscribe(camera, scheduler=CameraWorker.pool_scheduler)

    def is_eligible(self, photo, security_images) -> CameraResult:
        result = CameraResult(
            best_score=0,
            best_score_image=None,
        )
        avg_score = 0

        for idx, fixed_image in enumerate(security_images):
            score = self.compare_images(photo, fixed_image['content'])
            avg_score += score

            self.logger.info(f"score: {score}, img: ${fixed_image['path']}")

            if score > result.best_score:
                result = CameraResult(
                    best_score=score,
                    best_score_image=fixed_image['content'],
                    taken_photo=photo
                )

        self.logger.info(f"final score: {result.best_score}")
        self.logger.info(f"avg score: {avg_score / len(security_images)}")

        return result

    def to_gray(self, image):
        # Check if the image is already grayscale
        if len(image.shape) == 2 or image.shape[2] == 1:
            return image
        else:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # def compare_images(self, image1, image2):
    #     # Convert images to grayscale for feature detection
    #     gray1 = self.to_gray(image1)
    #     gray2 = self.to_gray(image2)
    #
    #     # Initialize the ORB detector
    #     orb = cv2.ORB_create()
    #
    #     # Detect keypoints and compute descriptors
    #     kp1, des1 = orb.detectAndCompute(image1, None)
    #     kp2, des2 = orb.detectAndCompute(gray2, None)
    #
    #     # Check if descriptors are found
    #     if des1 is None or des2 is None:
    #         return 0
    #
    #     # Create a Brute-Force Matcher object with Hamming distance (suitable for ORB)
    #     bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    #     matches = bf.match(des1, des2)
    #
    #     # Sort matches based on distance. Lower distance means better match.
    #     matches = sorted(matches, key=lambda x: x.distance)
    #
    #     # Filter for good matches based on a distance threshold (you can adjust the threshold)
    #     good_matches = [m for m in matches if m.distance < 50]
    #
    #     # Return the number of good matches as a similarity score
    #     return len(good_matches)

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
                raise ValueError(f"Não foi possível abrir a câmera")

            time.sleep(1)

            for _ in range(5):
                cap.read()

            time.sleep(1)

            ret, frame = cap.read()

            if not ret or frame is None:
                raise ValueError(f"Não foi possível abrir a câmera")

            # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            curr_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            cv2.imwrite(f"/tmp/photo_{curr_datetime}.jpg", frame)

            return frame
        except Exception as e:
            self.logger.error(e)

        finally:
            cap.release()

    def load_security_images(self):
        fixed_image_paths = glob.glob("./assets/images/security-camera-images/*.png")
        images = []

        for image in fixed_image_paths:
            loaded = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
            if loaded is not None:
                images.append({
                    'path': image,
                    'content': loaded
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