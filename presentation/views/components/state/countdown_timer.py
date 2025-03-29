from tkinter import StringVar
from typing import Callable

from presentation.views.components.layout.text import Text


class CountdownTimer(Text):
    def __init__(self,
                 initial_value,
                 text_builder: Callable[[int], str],
                 on_reached_zero: Callable[[], None],
                 app,
                 autostart=True,
                 **kwargs):
        self.text = StringVar(value=text_builder(initial_value))
        super().__init__(label=self.text, **kwargs)
        self.app = app
        self.initial_value = initial_value
        self.current_value = initial_value
        self.text_builder = text_builder
        self.widget = None
        self.has_reached_zero = False
        self.autostart = autostart
        self.on_reached_zero = on_reached_zero

        if autostart:
            self.start()

    def start(self):
        self.app.after(1000, self.countdown)

    def restart(self):
        self.current_value = self.initial_value
        self.countdown()

    def countdown(self):
        if self.widget is None:
            self.app.after(1000, self.countdown)
            return

        if self.has_reached_zero or not self.widget.winfo_exists() or self.current_value == 0:
            return

        if self.current_value == 1:
            self.has_reached_zero = True
            self.on_reached_zero()
            return

        self.current_value -= 1
        self.text.set(self.text_builder(self.current_value))
        self.app.after(1000, self.countdown)

    def build(self, parent=None):
        self.widget = super().build(parent=parent)
        return self.widget

    def cancel(self):
        self.has_reached_zero = True
        self.current_value = 0
