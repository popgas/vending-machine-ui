import pathlib

class GeistFont:
    @staticmethod
    def regular():
        return GeistFont.load("Geist-Regular")

    @staticmethod
    def light():
        return GeistFont.load("Geist-Light")

    @staticmethod
    def extra_light():
        return GeistFont.load("Geist-ExtraLight")

    @staticmethod
    def thin():
        return GeistFont.load("Geist-Thin")

    @staticmethod
    def medium():
        return GeistFont.load("Geist-Medium")

    @staticmethod
    def semi_bold():
        return GeistFont.load("Geist-SemiBold")

    @staticmethod
    def bold():
        return GeistFont.load("Geist-Bold")

    @staticmethod
    def extra_bold():
        return GeistFont.load("Geist-ExtraBold")

    @staticmethod
    def black():
        return GeistFont.load("Geist-Black")

    @staticmethod
    def load(name):
        curr_dir = pathlib.Path().parent.resolve()
        print("Current directory:", curr_dir)
        # In PyQt6, you might load a TTF file dynamically. Tkinter cannot do that directly.
        # Instead, the font must be installed on your system.
        # For this example, we assume that the custom Geist font is installed and its family name is the same as `name`.
        return name
