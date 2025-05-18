from presentation.views.components.layout.column import Column
from presentation.views.components.layout.contracts.buildable_widget import BuildableWidget
from presentation.views.components.layout.enums.alignment import Anchor, Side
from presentation.views.components.layout.icon import Icon
from presentation.views.components.layout.image import ImageFromAssets
from presentation.views.components.layout.padding import Padding
from presentation.views.components.layout.row import Row
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.text import Text
from application import Application
from utils.file import FileUtils
import tkinter as tk
from tkinter.messagebox import showinfo


class TransparentTopBar(BuildableWidget):
    def __init__(self, app: Application, can_pop=False):
        self.app = app
        self.can_pop = can_pop

    def build(self, parent=None):
        trailing = []

        if self.can_pop:
            trailing.append(
                Icon(
                    "arrow-left",
                    anchor=Anchor.LEFT,
                    width=30,
                    height=34
                ),
            )
        else:
            trailing.append(
                SizedBox(width=30)
            )

        row = Column(
            padding=Padding.all(20),
            children=[
                Row(
                    anchor=Anchor.LEFT,
                    children=[
                        Row(
                            children=trailing,
                            on_click=self.app.pop,
                            anchor=Anchor.LEFT
                        ),
                        Row(
                            children=[
                                ImageFromAssets(
                                    path=f"{FileUtils.root()}/assets/images/colored-logo.png",
                                    width=80,
                                    height=45,
                                    side=Side.TOP,
                                    anchor=Anchor.CENTER,
                                    padding=Padding(left=30),
                                ),
                            ]
                        ),
                        Row(
                            children=[
                                Column(
                                    children=[
                                        Icon("phone", anchor=tk.CENTER, width=30, height=30, side=Side.TOP),
                                        Text("Suporte")
                                    ],
                                    on_click=lambda: self.on_click(),
                                    side=Side.RIGHT,
                                    anchor=Anchor.TOP_RIGHT,
                                )
                            ]
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
        self.app.pop()