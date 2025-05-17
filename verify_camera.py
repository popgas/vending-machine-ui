from infrastructure.hardware.camera import CameraWorker, CameraResult

if __name__ == '__main__':
    CameraWorker.start(
        camera_socket="/dev/v4l/by-path/platform-3f980000.usb-usb-0:1.3:1.0-video-index0",
        on_completed=lambda r: Teste.handle_camera_callback(r),
    )

class Teste:
    @staticmethod
    def handle_camera_callback(result: CameraResult) -> None:
        pass