from presentation.config.color_palette import ColorPalette
from presentation.views.components.dialogs.info_dialog import InfoDialog
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets
from presentation.views.components.layout.padding import Padding
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.text import Text
from router import Router
from utils.file import FileUtils
import tkinter as tk
from tkinter.messagebox import showinfo


class TransparentTopBar(BuildableWidget):
    def __init__(self, router: Router, can_pop=False):
        self.router = router
        self.can_pop = can_pop

    def build(self, parent=None):
        trailing = []

        # if self.can_pop:
        #     trailing.append(
        #         Icon("fa6s.arrow-left",
        #              color=ColorPalette.blue3,
        #              size=30)
        #     )

        row = Column(
            padding=Padding.all(20),
            children=[
                Row(
                    anchor=tk.W,
                    children=[
                        Row(
                            children=[
                                ImageFromAssets(
                                    path=f"{FileUtils.root()}/assets/images/colored-logo.png",
                                    size=80,
                                    anchor=tk.CENTER,
                                    padding=Padding(left=80)
                                ),
                            ]
                        ),
                        Column(
                            children=[
                                Icon("phone", anchor=tk.CENTER),
                                Text("Suporte")
                            ],
                            on_click=lambda: self.on_click(),
                            side=tk.RIGHT,
                            anchor=tk.NE,
                        )
                    ],
                )
            ]
        )

        return row.build(parent=parent)

    def on_click(self):
        showinfo(
            title='Suporte Técnico',
            message="Para entrar em contato conosco:\n\nTelefone ou Whatsapp:\n0800 740 7070"
        )

    def pop_route(self):
        self.router.pop()