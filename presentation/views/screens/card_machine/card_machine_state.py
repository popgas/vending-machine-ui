from presentation.views.core.state_notifier import StateNotifier


class CardMachineState(StateNotifier):
    def __init__(self):
        super().__init__()
        self.awaiting_payment_approval = True
        self.rejected = False


    def update(self, awaiting_payment_approval=None, rejected=None):
        if awaiting_payment_approval is not None:
            self.awaiting_payment_approval = awaiting_payment_approval

        if rejected is not None:
            self.rejected = rejected

        self.notify()