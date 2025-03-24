import pathlib

from PyQt6.QtGui import QFontDatabase


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
        print(curr_dir)
        font_id = QFontDatabase.addApplicationFont(f"{curr_dir}/assets/fonts/non.geist/{name}.ttf")
        return QFontDatabase.applicationFontFamilies(font_id)[0]