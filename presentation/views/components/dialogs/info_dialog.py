from tkinter import Toplevel

from presentation.views.components.layout.button import Button
from presentation.views.components.layout.column import Column
from presentation.views.components.layout.sized_box import SizedBox
from presentation.views.components.layout.text import Text

class InfoDialog:
    def __init__(self, title="Informação", message=None):
        self.parent = parent
        self.top = Toplevel(parent)
        self.top.title(title)
        # Remove the window decorations (frameless)
        self.top.overrideredirect(True)
        # Set the dialog as transient and modal.
        self.top.transient(parent)
        self.top.grab_set()

        # Set a basic style: white background, gray border.
        self.top.configure(bg="#fff", highlightthickness=1, highlightbackground="#bbb")

        # Create content using your layout components.
        content = Column(
            children=[
                Text(message, alignment=alignment, font_size=20),
                SizedBox(height=24),
                Button(
                    label="Entendi",
                    font_size=15,
                    background_color="#007ACC",
                    border_radius=5,  # Note: border radius may require extra work in Tkinter.
                    on_click=self.accept
                )
            ]
        ).build(parent=self.top)

        # Pack the content to fill the dialog.
        content.pack(fill="both", expand=True, padx=10, pady=10)

        # Center the dialog over the parent.
        self.center_dialog()

    def center_dialog(self):
        self.parent.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        self.top.update_idletasks()
        dialog_width = self.top.winfo_width()
        dialog_height = self.top.winfo_height()

        pos_x = parent_x + (parent_width - dialog_width) // 2
        pos_y = parent_y + (parent_height - dialog_height) // 2

        self.top.geometry(f"{dialog_width}x{dialog_height}+{pos_x}+{pos_y}")

    def accept(self):
        self.top.destroy()

    def exec(self):
        # Wait until the dialog is closed.
        self.parent.wait_window(self.top)
