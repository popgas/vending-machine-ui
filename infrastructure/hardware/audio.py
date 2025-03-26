import pygame
from PyQt6.QtCore import QTimer


class AudioWorker:
    @staticmethod
    def play(path):
        pygame.mixer.init()
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

    @staticmethod
    def delayed(path):
        QTimer.singleShot(200, lambda: AudioWorker.play(path))

    @staticmethod
    def stop():
        pygame.mixer.music.stop()