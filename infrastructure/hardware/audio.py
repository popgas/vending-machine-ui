import pygame
import rx
from rx.scheduler import ThreadPoolScheduler


class AudioWorker:
    pool_scheduler = ThreadPoolScheduler(1)

    @staticmethod
    def play(path):
        AudioWorker.__play_audio(path)
        # return
        # rx.return_value(path).subscribe(
        #     on_next=AudioWorker.__play_audio,
        #     on_completed= lambda: print("audio played"),
        #     on_error= lambda e: print(f"audio not played {e}"),
        #     scheduler=AudioWorker.pool_scheduler
        # )

    @staticmethod
    def __play_audio(path):
        print("playing", path)

        if pygame.mixer.get_init():
            pygame.mixer.quit()

        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)

        try:
            print("Tentando inicializar mixer com SDL_AUDIODRIVER =", pygame.get_sdl_audio_driver())
        except Exception:
            print("SDL_AUDIODRIVER não definido. Forçando 'alsa'.")

            import os
            os.environ["SDL_AUDIODRIVER"] = "alsa"
            print("SDL_AUDIODRIVER agora =", os.environ["SDL_AUDIODRIVER"])

        try:
            pygame.mixer.init()
            print("Mixer inicializado com sucesso.")
        except pygame.error as e:
            print(f"Erro ao inicializar mixer: {e}", file=sys.stderr)
            return

        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

    @staticmethod
    def stop():
        rx.return_value(None).subscribe(
            on_next=lambda e: pygame.mixer.music.stop(),
            on_completed= lambda: print("audio stopped"),
            on_error= lambda e: print(f"audio not stopped {e}"),
            scheduler= AudioWorker.pool_scheduler,
        )
