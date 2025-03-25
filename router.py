from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget

class Router(QMainWindow):
    def __init__(self, application):
        super().__init__()
        self.application = application
        self.setWindowTitle("Navigation Stack Example")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.setContentsMargins(0,0,0,0)
        self.threadpool = QThreadPool()

        # Navigation stack: list of widgets.
        self.nav_stack = []

    def push(self, widget: QWidget):
        """Push a new widget (screen) onto the navigation stack."""
        self.nav_stack.append(widget)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def pop(self):
        """Pop the current widget from the navigation stack and return to the previous one."""
        if len(self.nav_stack) <= 1:
            print("Cannot pop the last route.")
            return

        current_widget = self.nav_stack.pop()
        self.stack.removeWidget(current_widget)
        current_widget.deleteLater()  # Clean up the widget.
        self.stack.setCurrentWidget(self.nav_stack[-1])

    def clear_stack(self):
        """Remove all screens from the navigation stack."""
        while self.nav_stack:
            widget = self.nav_stack.pop()
            self.stack.removeWidget(widget)
            widget.deleteLater()
        print("Navigation stack cleared.")

    def off_all(self, widget: QWidget):
        """
        Remove all screens from the navigation stack and push a new one.
        Similar to Flutter's Get.offAll(() => WelcomeScreen()).
        """
        self.clear_stack()
        self.push(widget)

    def show_bg(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ECEFF1;
                background-image: url(./images/botijao_bg2.png);
                background-repeat: no-repeat;
                background-position: right bottom;
            }
        """)

    def hide_bg(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ECEFF1;
                background-image: none;
                background-repeat: no-repeat;
                background-position: right bottom;
            }
        """)