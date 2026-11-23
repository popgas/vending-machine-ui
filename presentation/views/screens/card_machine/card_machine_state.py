from presentation.views.core.state_notifier import StateNotifier


class CardMachineState(StateNotifier):
    def __init__(self):
        super().__init__()
        self.awaiting_payment_approval = True
        self.rejected = False
        self.timed_out = False
        self.remove_card_prompt = False


    def update(self, awaiting_payment_approval=None, rejected=None, timed_out=None, remove_card_prompt=None):
        if awaiting_payment_approval is not None:
            self.awaiting_payment_approval = awaiting_payment_approval

        if rejected is not None:
            self.rejected = rejected

        if timed_out is not None:
            self.timed_out = timed_out

        if remove_card_prompt is not None:
            self.remove_card_prompt = remove_card_prompt

        self.notify()
