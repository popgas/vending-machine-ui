from presentation.views.core.state_notifier import StateNotifier


class OrderCompletedState(StateNotifier):
    def __init__(self):
        super().__init__()
        self.has_rated = False

    def update(self, has_rated=None):
        if has_rated is not None:
            self.has_rated = has_rated
        self.notify()