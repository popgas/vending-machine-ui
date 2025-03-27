from collections.abc import Callable

from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget


class Scaffold:
    def __init__(self, parent, child: BuildableWidget | Callable[[], BuildableWidget], state=None):
        """
        :param parent: The parent Tkinter widget.
        :param child: A buildable widget or a callable returning one.
        :param state: Optional state notifier with a subscribe(callback) method.
        """
        # Ensure child is callable.
        self.child = child if callable(child) else lambda: child
        self.parent = parent
        self.state = state
        self.build()

        if self.state is not None:
            self.state.subscribe(lambda: self.build())

    def build(self):
        self.child().build(parent=self.parent)
