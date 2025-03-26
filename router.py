from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout


class Router(QMainWindow):
    def __init__(self, application, routes: dict[str, callable]):
        super().__init__()
        self.application = application
        self.setWindowTitle("Navigation Stack Example")

        self.stack = QStackedWidget()

        layout = QVBoxLayout(self.stack)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setCentralWidget(self.stack)

        self.setContentsMargins(0,0,0,0)
        self.threadpool = QThreadPool()

        # Navigation stack: list of widgets.
        self.nav_stack = []
        self.routes = routes

    def push(self, name: str, *args):
        """Push a new widget (screen) onto the navigation stack."""
        widget = self.routes[name](self, *args)
        self.nav_stack.append(widget)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def pop(self):
        """Pop the current widget from the navigation stack and return to the previous one."""
        if len(self.nav_stack) <= 1:
            print("Cannot pop the last route.")
            return

        current_widget = self.nav_stack.pop()
        previous = self.nav_stack[-1]

        self.stack.setCurrentWidget(previous)

        if hasattr(previous, 'on_route_popped') and callable(previous.on_route_popped):
            self.nav_stack[-1].on_route_popped()

        self.stack.removeWidget(current_widget)
        current_widget.deleteLater()  # Clean up the widget.

    def clear_stack(self):
        """Remove all screens from the navigation stack."""
        while self.nav_stack:
            widget = self.nav_stack.pop()
            self.stack.removeWidget(widget)
            widget.deleteLater()
        print("Navigation stack cleared.")

    def off_all(self, name: str):
        """
        Remove all screens from the navigation stack and push a new one.
        Similar to Flutter's Get.offAll(() => WelcomeScreen()).
        """
        self.clear_stack()
        self.push(name)

    def show_bg(self):
        self.setStyleSheet("""
            QMainWindow {
                padding: 0px;
                background-color: #ECEFF1;
                background-image: url(./assets/images/botijao_bg2.png);
                background-repeat: no-repeat;
                background-position: right bottom;
            }
        """)

    def hide_bg(self):
        self.setStyleSheet("""
            QMainWindow {
                padding: 0px;
                background-color: #ECEFF1;
                background-image: none;
                background-repeat: no-repeat;
                background-position: right bottom;
            }
        """)