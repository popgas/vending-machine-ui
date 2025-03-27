from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.button import Button


class BlueButton(Button):
    def __init__(self, label="Blue Button", font_size=40, on_click=None):
        super().__init__(
            label=label,
            font_size=font_size,
            border_radius=5,
            color="#fff",
            on_click=on_click,
            background_color=ColorPalette.blue3,
            pressed_background_color=ColorPalette.blue2,
            pressed_color="#fff"
        )