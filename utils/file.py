import pathlib


class FileUtils:
    @staticmethod
    def dir(filename):
        return pathlib.Path(filename).parent.resolve()