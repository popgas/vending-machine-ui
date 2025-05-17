from infrastructure.hardware.camera import CameraWorker, CameraResult

if __name__ == '__main__':
    CameraWorker.start(
        camera_socket=0,
        on_completed=lambda r: Teste.handle_camera_callback(r),
    )

class Teste:
    @staticmethod
    def handle_camera_callback(result: CameraResult) -> None:
        pass