from presentation.views.core.state_notifier import StateNotifier


class PlaceEmptyContainerState(StateNotifier):
    def __init__(self):
        super().__init__()
        self.closing_door = False
        self.cancelling = False

    def update(self, closing_door=None, cancelling=None):
        if closing_door is not None:
            self.closing_door = closing_door

        if cancelling is not None:
            self.cancelling = cancelling

        self.notify()


class PlaceEmptyContainerTimerState(StateNotifier):
    def __init__(self):
        super().__init__()
        self.timer_reached_zero = False
        self.time_to_close_door_automatically = 120

    def update(self,
               timer_reached_zero=None,
               time_to_close_door_automatically=None):
        if timer_reached_zero is not None:
            self.timer_reached_zero = timer_reached_zero

        if time_to_close_door_automatically is not None:
            self.time_to_close_door_automatically = time_to_close_door_automatically

        self.notify()
