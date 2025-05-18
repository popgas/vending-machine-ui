import os
import tkinter as tk

from infrastructure.http.popgas_api import PopGasApi
from presentation.config.color_palette import ColorPalette
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.enums.alignment import Anchor, Side
from presentation.views.components.layout.image import ImageFromAssets
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.spacer import SpacerVertical
from presentation.views.components.layout.text import Text
from presentation.views.components.scaffold.state_provider import StateProvider
from presentation.views.components.scaffold.transparent_top_bar import TransparentTopBar
from application import Application
from utils.file import FileUtils


class TechSupportScreen(tk.Frame):
    def __init__(self, app: Application):
        super().__init__(app.container, bg="#FFFFFF")
        self.app = app

        StateProvider(
            parent=self,
            child=Column(
                expand=True,
                anchor=Anchor.CENTER,
                children=[
                    TransparentTopBar(app),
                    Column(
                        expand=True,
                        children=[
                            SpacerVertical(),
                            ImageFromAssets(
                                path=f"{FileUtils.dir(__file__)}/assets/disruption.png",
                                width=150,
                                height=150,
                                side=Side.TOP,
                                anchor=Anchor.CENTER,
                            ),
                            SizedBox(height=100),
                            Text("Problemas Técnicos", font_size=35, color=ColorPalette.blue3),
                            SizedBox(height=40),
                            Text("A máquina está fora do ar por problemas", font_size=24, color=ColorPalette.blue3),
                            Text("técnicos. Uma equipe já foi acionada e", font_size=24, color=ColorPalette.blue3),
                            Text("em breve o problema será resolvido.", font_size=24, color=ColorPalette.blue3),
                            SpacerVertical(),
                        ],
                        anchor=Anchor.CENTER,
                    ),
                ],
            )
        )

        self.timer = self.app.after(5 * 1000, self.check_tech_support)

    def check_tech_support(self):
        vm_id = os.environ['VENDING_MACHINE_ID']
        response = PopGasApi.request("GET", f"/vending-machine-orders/{vm_id}/prices").json()

        if 'is_under_maintenance' not in response or not bool(response['is_under_maintenance']):
            self.app.after_cancel(self.timer)
            self.app.off_all('welcome')
            return

        self.timer = self.app.after(120 * 1000, self.check_tech_support)