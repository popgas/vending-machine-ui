from presentation.views.core.state_notifier import StateNotifier


class CameraVerificationState(StateNotifier):
    def __init__(self):
        super().__init__()
        self.failed_security_check = False

    def update(self,
               failed_security_check=None):
        if failed_security_check is not None:
            self.failed_security_check = failed_security_check

        self.notify()