from presentation.views.core.state_notifier import StateNotifier


class PlaceEmptyContainerState(StateNotifier):
    def __init__(self):
        super().__init__()
        self.closing_door = False

    def update(self, closing_door=None):
        if closing_door is not None:
            self.closing_door = closing_door

        self.notify()