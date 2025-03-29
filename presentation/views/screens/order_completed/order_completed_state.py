from presentation.views.core.state_notifier import StateNotifier


class OrderCompletedState(StateNotifier):
    def __init__(self):
        super().__init__()
        self.has_rated = False
        self.closing_doors = False

    def update(self, has_rated=None, closing_doors=None):
        if has_rated is not None:
            self.has_rated = has_rated
        if closing_doors is not None:
            self.closing_doors = closing_doors
        self.notify()