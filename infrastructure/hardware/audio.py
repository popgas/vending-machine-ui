import pygame
from PyQt6.QtCore import QTimer


class AudioWorker:
    @staticmethod
    def play(path):
        QTimer.singleShot(100, lambda : AudioWorker.__delayedPlay(path))

    @staticmethod
    def __delayedPlay(path):
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
