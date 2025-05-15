from presentation.views.core.state_notifier import StateNotifier


class PaymentSelectionState(StateNotifier):
    def __init__(self):
        super().__init__()
        self.cancelling = False

    def update(self, cancelling=None):
        if cancelling is not None:
            self.cancelling = cancelling

        self.notify()