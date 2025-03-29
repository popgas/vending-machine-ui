from presentation.views.core.state_notifier import StateNotifier


class PlaceEmptyContainerState(StateNotifier):
    def __init__(self):
        super().__init__()
        self.closing_door = False
        self.cancelling = False
        self.timer_reached_zero = False

    def update(self, closing_door=None, timer_reached_zero=None, cancelling=None):
        if closing_door is not None:
            self.closing_door = closing_door

        if cancelling is not None:
            self.cancelling = cancelling

        if timer_reached_zero is not None:
            self.timer_reached_zero = timer_reached_zero

        self.notify()