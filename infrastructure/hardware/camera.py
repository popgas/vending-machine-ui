import glob

import cv2
from PyQt6.QtCore import QRunnable, pyqtSlot

from infrastructure.observability.logger import Logger


class CameraWorker(QRunnable):
    def __init__(self, callback):
        super().__init__()
        self.logger = Logger.get_logger()
        self.callback = callback

    @pyqtSlot()
    def run(self):
        try:
            security_images = self.load_security_images()
            photo = self.take_photo()

            is_eligible = self.is_eligible(photo, security_images)

            self.callback(is_eligible)

        except Exception as e:
            print(e)
            self.callback(False)

    def is_eligible(self, photo, security_images):
        best_score = 0

        for idx, fixed_image in enumerate(security_images):
            score = self.compare_images(photo, fixed_image)

            print(f"score: {score}, image={fixed_image}")

            if score > best_score:
                best_score = score

        print(f"final score: {best_score}")

        return best_score >= 40

    def to_gray(self, image):
        # Check if the image is already grayscale
        if len(image.shape) == 2 or image.shape[2] == 1:
            return image
        else:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def compare_images(self, image1, image2):
        # Convert images to grayscale for feature detection
        gray1 = self.to_gray(image1)
        gray2 = self.to_gray(image2)

        # Initialize the ORB detector
        orb = cv2.ORB_create()

        # Detect keypoints and compute descriptors
        kp1, des1 = orb.detectAndCompute(image1, None)
        kp2, des2 = orb.detectAndCompute(gray2, None)

        # Check if descriptors are found
        if des1 is None or des2 is None:
            return 0

        # Create a Brute-Force Matcher object with Hamming distance (suitable for ORB)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        # Sort matches based on distance. Lower distance means better match.
        matches = sorted(matches, key=lambda x: x.distance)

        # Filter for good matches based on a distance threshold (you can adjust the threshold)
        good_matches = [m for m in matches if m.distance < 50]

        # Return the number of good matches as a similarity score
        return len(good_matches)

    def take_photo(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            raise ValueError(f"Não foi possível abrir a câmera")

        cv2.waitKey(100)
        ret, frame = cap.read()

        if not ret:
            raise ValueError(f"Não foi possível abrir a câmera")

        cap.release()

        return frame

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