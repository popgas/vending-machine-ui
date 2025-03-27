from presentation.views.components.layout.image import ImageFromAssets
from utils.file import FileUtils

class Icon(ImageFromAssets):
    def __init__(self, icon=None, width=23, **kargs):
        super().__init__(
            f"{FileUtils.root()}/assets/icons/{icon}.png",
            width=width,
            **kargs
        )
