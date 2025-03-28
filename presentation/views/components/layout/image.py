import tkinter as tk
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.enums.alignment import Anchor, Side
from presentation.views.components.layout.padding import Padding
from PIL import Image, ImageTk, ImageSequence

from utils.file import FileUtils


class ImageFromAssets(BuildableWidget):
    def __init__(self, path, width=80, height=80, side=Side.LEFT, anchor=Anchor.LEFT, padding: Padding = None):
        self.path = path
        self.width = width
        self.height = height
        self.anchor = anchor
        self.side = side
        self.img = None
        self.padding = padding or Padding.zero()

    def build(self, parent=None):
        original_image = Image.open(self.path)
        resized_image = original_image.resize((self.width, self.height))  # Width, Height

        tk_image = ImageTk.PhotoImage(resized_image)

        label = tk.Label(parent,
                         width=self.width,
                         height=self.height,
                         image=tk_image,
                         bg=parent['bg'])
        label.image = tk_image
        label.pack(
            anchor=self.anchor,
            side=self.side,
            expand=False,
            fill=tk.NONE,
            padx=self.padding.padx,
            pady=self.padding.pady,
        )

        return label

class CircularSpinner(BuildableWidget):
    def __init__(self, root, **kwargs):
        self.root = root
        self.path = f"{FileUtils.root()}/assets/images/spinner.gif"
        self.frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(Image.open(self.path))]
        self.index = 0
        self.image = ImageFromAssets(
             path=self.path,
             **kwargs
         )

    def build(self, parent=None):
        self.image = self.image.build(parent)
        self.animate()

    def animate(self):
        self.image.config(image=self.frames[self.index])
        self.index = (self.index + 1) % len(self.frames)
        self.root.after(30, self.animate)