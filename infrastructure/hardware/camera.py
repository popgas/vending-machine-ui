import glob
from typing import Callable

import cv2
import numpy as np
import rx
from rx.core.typing import Observer, T_in
from rx.scheduler import ThreadPoolScheduler

from infrastructure.observability.logger import Logger

class CameraResult:
    def __init__(self, best_score=0, best_score_image=None):
        self.best_score = best_score
        self.best_score_image = best_score_image

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
            print(e)

    def on_error(self, error: Exception) -> None:
        print(error)

    def on_completed(self) -> None:
        print(f"on_completed called {self.result}")

    @staticmethod
    def start(camera_socket, on_completed: Callable[[CameraResult], None]):
        camera = CameraWorker(camera_socket=camera_socket, on_completed=on_completed)

        rx.just(None).subscribe(camera, scheduler=CameraWorker.pool_scheduler)

    def is_eligible(self, photo, security_images) -> CameraResult:
        result = CameraResult(
            best_score=0,
            best_score_image=None,
        )

        for idx, fixed_image in enumerate(security_images):
            score = self.compare_images(photo, fixed_image)

            print(f"score: {score}")

            if score > result.best_score:
                result = CameraResult(
                    best_score=score,
                    best_score_image=fixed_image,
                )

        print(f"final score: {result.best_score}")

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

        if not cap.isOpened():
            raise ValueError(f"Não foi possível abrir a câmera")

        cv2.waitKey(100)
        ret, frame = cap.read()

        if not ret:
            raise ValueError(f"Não foi possível abrir a câmera")

        cap.release()

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        return gray_frame

    def load_security_images(self):
        fixed_image_paths = glob.glob("./assets/images/security-camera-images/*.png")
        images = []

        for image in fixed_image_paths:
            loaded = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
            if loaded is not None:
                images.append(loaded)
                self.logger.info(f"Imagem carregada: {image}")
            else:
                self.logger.error(f"Erro ao carregar a imagem: {image}")

        if not images:
            self.logger.warning("Nenhuma imagem válida foi encontrada na pasta.")

        return images