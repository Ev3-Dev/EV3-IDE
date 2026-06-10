import customtkinter as ctk

class Console:
    def __init__(self, root, console_height, register_layout_callback):
        # -------- Variablen --------
        self.root = root
        self.CONSOLE_HEIGHT = console_height
        self.register_layout_callback = register_layout_callback
        # -------- GUI-Elemente --------
        self.console = ctk.CTkTextbox(self.root, width=1318, height=self.CONSOLE_HEIGHT, corner_radius=7, fg_color="#1C1A1A", text_color="#D4D4D4", font=("JetBrains Mono", 15), spacing3=2)
        self.console.insert("1.0", "Select a file\n\n")
        self.console.configure(state="disabled")
        self.console.tag_config("stderr", foreground="#FF5555")
        self.console.place(x=596, y=self.root.winfo_height()-5, anchor="sw")
        # Callback hinzufügen
        self.register_layout_callback(self.update_layout)

    def update_layout(self, width, height, is_console_hidden, is_status_panel_hidden, event=None):
        if is_console_hidden:
            return
        if is_status_panel_hidden:
            new_width = width - 10
            self.console.configure(width=new_width)
            self.console.place(x=5, y=self.root.winfo_height()-5, anchor="sw")
        else:
            new_width = width - 587 - 15
            self.console.configure(width=new_width)
            self.console.place(x=596, y=self.root.winfo_height()-5, anchor="sw")

    def update_console(self, content):
        self.console.configure(state="normal")
        self.console.insert("end", content)
        self.console.configure(state="disabled")
        self.console.see("end")

    def update_console_std(self, std_type, content):
        self.console.configure(state="normal")
        start_index = self.console.index("end-1c")
        self.console.insert("end", content)
        end_index = self.console.index("end-1c")
        if std_type == "stderr":
            self.console.tag_add("stderr", start_index, end_index)
        self.console.configure(state="disabled")
        self.console.see("end")

    def program_finished(self):
        self.console.configure(state="normal")
        self.console.insert("end", "\n\nProgram finished\n\n")
        self.console.configure(state="disabled")
        self.console.see("end")

    def delete_all(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")