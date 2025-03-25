import sys
from PyQt6.QtWidgets import QApplication

from presentation.views.screens.welcome.welcome import WelcomeScreen
from router import Router

if __name__ == '__main__':
    app = QApplication(sys.argv)
    router = Router(app)

    # Start by pushing the welcome screen.
    router.push(WelcomeScreen(router))
    router.showFullScreen()
    sys.exit(app.exec())