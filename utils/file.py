import pathlib

class FileUtils:
    @staticmethod
    def dir(filename):
        return pathlib.Path(filename).parent.resolve()

    @staticmethod
    def root():
        return FileUtils.dir(__file__).parent