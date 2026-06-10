import customtkinter as ctk
from PIL import Image

class ContextPopUp:
    def __init__(self, root):
        self.root = root
        self.selected_path = None
        self.selected_type = None
        self.popup = None

    def show_context_menu(self, event, path, entry_type, context_open, context_rename, context_delete, context_execute):
        self.selected_path = path
        self.selected_type = entry_type

        # Falls schon ein Popup offen ist: schließen
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()

        # Falls weit unten: Prüfen, damit es nicht abgeschnitten wird
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        x = event.x_root
        y = event.y_root
        pop_up_height = 120
        spacer = 5
        if y + pop_up_height > root_y + root_height - spacer:
            y = y - pop_up_height

        self.popup = ctk.CTkFrame(self.root, height=pop_up_height, width=150, corner_radius=7, border_width=1, border_color="#3B3333", fg_color=["gray86", "gray17"], bg_color="#151313")
        self.popup.place(x=x-root_x, y=y-root_y)

        if entry_type == "file" and "." not in path:
            img = ctk.CTkImage(light_image=Image.open("images/execute_code.png"), dark_image=Image.open("images/execute_code.png"), size=(15, 15))
            btn_execute = ctk.CTkButton(self.popup, text="Execute", fg_color=["gray86", "gray17"], text_color="#D4D4D4", anchor="w", command=lambda: self._run(context_execute), image=img, corner_radius=7, hover_color="#606060")
            btn_execute.pack(fill="x", padx=4, pady=(4, 2))
        else:
            img = ctk.CTkImage(light_image=Image.open("images/open.png"), dark_image=Image.open("images/open.png"), size=(15, 15))
            btn_open = ctk.CTkButton(self.popup, text="Open", fg_color=["gray86", "gray17"], command=lambda: self._run(context_open), image=img, text_color="#D4D4D4", anchor="w", corner_radius=7, hover_color="#606060")
            btn_open.pack(fill="x", padx=4, pady=(4, 2))
        img = ctk.CTkImage(light_image=Image.open("images/rename.png"), dark_image=Image.open("images/rename.png"), size=(14, 14))
        btn_rename = ctk.CTkButton(self.popup, text="Rename", fg_color=["gray86", "gray17"], command=lambda: self._run(context_rename), image=img, text_color="#D4D4D4", anchor="w", corner_radius=7, hover_color="#606060")
        btn_rename.pack(fill="x", padx=4, pady=(2, 2))
        img = ctk.CTkImage(light_image=Image.open("images/delete.png"), dark_image=Image.open("images/delete.png"), size=(14, 14))
        btn_delete = ctk.CTkButton(self.popup, text="Delete", fg_color=["gray86", "gray17"], command=lambda: self._run(context_delete), image=img, text_color="#D4D4D4", anchor="w", corner_radius=7, hover_color="#944444")
        btn_delete.pack(fill="x", padx=4, pady=(2, 4))
        self.root.bind("<Button-1>", self._click_outside)

    def _click_outside(self, event):
        if self.popup:
            # Prüfen, ob Klick außerhalb des Frames ist
            x1 = self.popup.winfo_rootx()
            y1 = self.popup.winfo_rooty()
            x2 = x1 + self.popup.winfo_width()
            y2 = y1 + self.popup.winfo_height()
            if not (x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2):
                self.popup.destroy()
                self.popup = None
                self.root.unbind("<Button-1>")

    def _run(self, callback):
        callback(self.selected_type, self.selected_path)
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None
            self.root.unbind("<Button-1>")