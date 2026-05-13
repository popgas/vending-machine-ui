import pygame
import reactivex as rx
from reactivex.scheduler import ThreadPoolScheduler


class AudioWorker:
    pool_scheduler = ThreadPoolScheduler(1)

    @staticmethod
    def play(path):
        rx.just(path).subscribe(
            on_next=AudioWorker.__play_audio,
            on_completed= lambda: print("audio played"),
            on_error= lambda e: print(f"audio not played {e}"),
            scheduler=AudioWorker.pool_scheduler
        )

    @staticmethod
    def __play_audio(path):
        print("playing", path)

        pygame.mixer.init()
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

    @staticmethod
    def stop():
        rx.just(None).subscribe(
            on_next=lambda e: pygame.mixer.music.stop(),
            on_completed= lambda: print("audio stopped"),
            on_error= lambda e: print(f"audio not stopped {e}"),
            scheduler= AudioWorker.pool_scheduler,
        )
