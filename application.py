import tkinter as tk


class Application(tk.Tk):
    def __init__(self, routes: dict[str, callable]):
        super().__init__()
        self.title("PopGás Auto Atendimento 24h")
        self.routes = routes
        self.nav_stack = []
        self.nav_stack_names = []

        # Create a container frame to act like a stacked widget.
        self.container = tk.Frame(self, bg="#FFFFFF")
        self.container.pack(fill="both", expand=True)

        # To simulate threadpool functionality in PyQt, you might use Python threads,
        # but for this example we'll omit that functionality.

    def push(self, name: str, *args):
        if len(self.nav_stack_names) > 0 and self.nav_stack_names[-1] == name:
            print("duplicated!")
            return

        """Push a new widget (screen) onto the navigation stack."""
        screen_constructor = self.routes.get(name)

        if screen_constructor:
            widget = screen_constructor(self, *args)
            self.nav_stack.append(widget)
            self.nav_stack_names.append(name)

            widget.place(x=0, y=0, anchor="nw", relheight=1.0, relwidth=1.0)
            widget.tkraise()

            if hasattr(widget, 'on_route_mounted') and callable(widget.on_route_mounted):
                widget.on_route_mounted()

        else:
            print("Screen not found:", name)

    def pop(self):
        """Pop the current widget from the navigation stack and return to the previous one."""
        if len(self.nav_stack) <= 1:
            print("Cannot pop the last route.")
            return

        self.nav_stack_names.pop()
        current_widget = self.nav_stack.pop()

        if hasattr(current_widget, 'dispose') and callable(current_widget.dispose):
            current_widget.dispose()

        # Remove the current widget.
        current_widget.destroy()
        # Bring the previous screen to the front.
        previous = self.nav_stack[-1]
        previous.tkraise()

        # If the previous screen has an on_route_popped method, call it.
        if hasattr(previous, 'on_route_popped') and callable(previous.on_route_popped):
            previous.on_route_popped()

    def clear_stack(self):
        """Remove all screens from the navigation stack."""
        while self.nav_stack:
            widget = self.nav_stack.pop()
            widget.destroy()

        self.nav_stack_names = []
        print("Navigation stack cleared.")

    def off_all(self, name: str):
        """
        Remove all screens from the navigation stack and push a new one.
        Similar to Flutter's Get.offAll(() => WelcomeScreen()).
        """
        self.clear_stack()
        self.push(name)

    def show_bg(self):
        """
        Set a background style. In Tkinter, applying a background image requires more setup,
        such as placing a Label or Canvas behind other widgets.
        Here, we'll set a background color and leave a note for further enhancement.
        """
        self.configure(bg="#FFFFFF")
        # For an image background, you might create a Label with the image and place it
        # behind all other widgets using place().

    def hide_bg(self):
        """Remove the background image (or reset the background)."""
        self.configure(bg="#FFFFFF")  # Reset to the base background color.