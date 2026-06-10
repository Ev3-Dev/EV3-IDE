import customtkinter as ctk

class PopUpWindow:
    def __init__(self, root):
        self.root = root

    def create_overlay(self, header, ev3_path, callback):
        self.ev3_path = ev3_path
        self.overlay = ctk.CTkFrame(self.root, fg_color="#1C1A1A")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.pop_up_frame = ctk.CTkFrame(self.overlay, width=450, height=300, corner_radius=10)
        self.pop_up_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.header_label = ctk.CTkLabel(self.pop_up_frame, text=header, text_color="#D4D4D4", font=("Segoe UI", 24, "bold"), fg_color=("gray86", "gray17"), bg_color=("gray86", "gray17"))
        self.header_label.place(relx=0.5, rely=0.1, anchor="center")
        self.path_label = ctk.CTkLabel(self.pop_up_frame, text=f"Path:", text_color="#D4D4D4", font=("Segoe UI", 16))
        self.path_label.place(x=30, y=105)
        self.ev3_path_label = ctk.CTkLabel(self.pop_up_frame, text=f"{self.ev3_path}", text_color="#D4D4D4", font=("Segoe UI", 16))
        self.ev3_path_label.place(x=100, y=105)
        self.name_label = ctk.CTkLabel(self.pop_up_frame, text=f"Name:", text_color="#D4D4D4", font=("Segoe UI", 16))
        self.name_label.place(x=30, y=145)
        self.name_entry = ctk.CTkEntry(self.pop_up_frame, width=200, font=("Segoe UI", 16))
        self.name_entry.place(x=98, y=145)
        self.accept_button = ctk.CTkButton(self.pop_up_frame, text="OK", text_color="#D4D4D4", font=("Segoe UI", 15), fg_color=("#36719F", "#144870"), corner_radius=6, height=30, width=100, command=lambda: self.new_file(callback))
        self.accept_button.place(x=327, y=250)
        self.cancel_button = ctk.CTkButton(self.pop_up_frame, text="Cancel", text_color="#D4D4D4", font=("Segoe UI", 15), fg_color=("gray86", "gray17"), corner_radius=6, height=30, width=100, command=self.destroy_pop_up, border_width=1, border_color="#A0A0A0", hover_color=("gray86", "gray17"))
        self.cancel_button.place(x=215, y=250)
        # Key-Bindings
        self.name_entry.bind("<Control-BackSpace>", lambda event=None: self.name_entry.delete(0, "end"))
        self.name_entry.bind("<KeyRelease>", self.update_path_label, add="+")
        self.name_entry.bind("<Return>", lambda event=None: self.new_file(callback), add="+")
        self.root.bind_all("<Escape>", self.destroy_pop_up)

    def create_compile_overlay(self, ev3_path, callback):
        self.input_path = ev3_path
        self.compile_overlay = ctk.CTkFrame(self.root, fg_color="#1C1A1A")
        self.compile_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.compile_pop_up_frame = ctk.CTkFrame(self.compile_overlay, width=450, height=300, corner_radius=10)
        self.compile_pop_up_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.compile_header_label = ctk.CTkLabel(self.compile_pop_up_frame, text="Compile script", text_color="#D4D4D4", font=("Segoe UI", 24, "bold"), fg_color=("gray86", "gray17"), bg_color=("gray86", "gray17"))
        self.compile_header_label.place(relx=0.5, rely=0.1, anchor="center")
        self.compile_path_label = ctk.CTkLabel(self.compile_pop_up_frame, text="Output file path:", text_color="#D4D4D4", font=("Segoe UI", 16))
        self.compile_path_label.place(x=30, y=130)
        self.compile_name_entry = ctk.CTkEntry(self.compile_pop_up_frame, width=200, font=("Segoe UI", 16))
        self.compile_name_entry.place(x=155, y=130)
        self.compile_accept_button = ctk.CTkButton(self.compile_pop_up_frame, text="OK", text_color="#D4D4D4", font=("Segoe UI", 15), fg_color=("#36719F", "#144870"), corner_radius=6, height=30, width=100, command=lambda: self.compile(callback))
        self.compile_accept_button.place(x=327, y=250)
        self.compile_cancel_button = ctk.CTkButton(self.compile_pop_up_frame, text="Cancel", text_color="#D4D4D4", font=("Segoe UI", 15), fg_color=("gray86", "gray17"), corner_radius=6, height=30, width=100, command=self.destroy_compile_pop_up, border_width=1, border_color="#A0A0A0", hover_color=("gray86", "gray17"))
        self.compile_cancel_button.place(x=215, y=250)
        # Key-Bindings
        self.compile_name_entry.bind("<Control-BackSpace>", lambda event=None: self.compile_name_entry.delete(0, "end"))
        self.compile_name_entry.bind("<Return>", lambda event=None: self.compile(callback), add="+")
        self.root.bind_all("<Escape>", self.destroy_compile_pop_up)

    def create_confirm_overlay(self, ev3_path, callback):
        self.input_path = ev3_path
        self.confirm_overlay = ctk.CTkFrame(self.root, fg_color="#1C1A1A")
        self.confirm_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.confirm_pop_up_frame = ctk.CTkFrame(self.confirm_overlay, width=450, height=300, corner_radius=10)
        self.confirm_pop_up_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.confirm_header_label = ctk.CTkLabel(self.confirm_pop_up_frame, text="Delete path", text_color="#D4D4D4", font=("Segoe UI", 24, "bold"), fg_color=("gray86", "gray17"), bg_color=("gray86", "gray17"))
        self.confirm_header_label.place(relx=0.5, rely=0.1, anchor="center")
        self.confirm_path_label = ctk.CTkLabel(self.confirm_pop_up_frame, text=f"File path: {ev3_path}", text_color="#D4D4D4", font=("Segoe UI", 16))
        self.confirm_path_label.place(x=30, y=97)
        self.confirm_text_1_label = ctk.CTkLabel(self.confirm_pop_up_frame, text="Are you sure you want to delete this item?", text_color="#D4D4D4", font=("Segoe UI", 16))
        self.confirm_text_1_label.place(x=30, y=143)
        self.confirm_text_2_label = ctk.CTkLabel(self.confirm_pop_up_frame, text="This action cannot be undone", text_color="#D4D4D4", font=("Segoe UI", 16))
        self.confirm_text_2_label.place(x=30, y=168)
        self.confirm_accept_button = ctk.CTkButton(self.confirm_pop_up_frame, text="Yes", text_color="#D4D4D4", font=("Segoe UI", 15), fg_color=("#36719F", "#144870"), corner_radius=6, height=30, width=100, command=lambda: self.confirm(callback))
        self.confirm_accept_button.place(x=327, y=250)
        self.confirm_cancel_button = ctk.CTkButton(self.confirm_pop_up_frame, text="No", text_color="#D4D4D4", font=("Segoe UI", 15), fg_color=("gray86", "gray17"), corner_radius=6, height=30, width=100, command=self.destroy_confirm_pop_up, border_width=1, border_color="#A0A0A0", hover_color=("gray86", "gray17"))
        self.confirm_cancel_button.place(x=215, y=250)
        # Key-Bindings
        self.root.bind_all("<Return>", lambda event=None: self.confirm(callback))
        self.root.bind_all("<Escape>", self.destroy_confirm_pop_up)

    def create_rename_overlay(self, old_ev3_path, callback):
        self.old_ev3_path = old_ev3_path
        self.rename_overlay = ctk.CTkFrame(self.root, fg_color="#1C1A1A")
        self.rename_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.rename_pop_up_frame = ctk.CTkFrame(self.rename_overlay, width=450, height=300, corner_radius=10)
        self.rename_pop_up_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.header_label = ctk.CTkLabel(self.rename_pop_up_frame, text="Rename path", text_color="#D4D4D4", font=("Segoe UI", 24, "bold"), fg_color=("gray86", "gray17"), bg_color=("gray86", "gray17"))
        self.header_label.place(relx=0.5, rely=0.1, anchor="center")
        self.path_label = ctk.CTkLabel(self.rename_pop_up_frame, text=f"Old path:       {old_ev3_path}", text_color="#D4D4D4", font=("Segoe UI", 16))
        self.path_label.place(x=30, y=105)
        self.name_label = ctk.CTkLabel(self.rename_pop_up_frame, text=f"New path:", text_color="#D4D4D4", font=("Segoe UI", 16))
        self.name_label.place(x=30, y=145)
        self.name_entry = ctk.CTkEntry(self.rename_pop_up_frame, width=200, font=("Segoe UI", 16))
        self.name_entry.place(x=118, y=145)
        self.accept_button = ctk.CTkButton(self.rename_pop_up_frame, text="OK", text_color="#D4D4D4", font=("Segoe UI", 15), fg_color=("#36719F", "#144870"), corner_radius=6, height=30, width=100, command=lambda: self.rename(callback))
        self.accept_button.place(x=327, y=250)
        self.cancel_button = ctk.CTkButton(self.rename_pop_up_frame, text="Cancel", text_color="#D4D4D4", font=("Segoe UI", 15), fg_color=("gray86", "gray17"), corner_radius=6, height=30, width=100, command=self.destroy_rename_pop_up, border_width=1, border_color="#A0A0A0", hover_color=("gray86", "gray17"))
        self.cancel_button.place(x=215, y=250)
        # Key-Bindings
        self.name_entry.bind("<Control-BackSpace>", lambda event=None: self.name_entry.delete(0, "end"))
        self.name_entry.bind("<Return>", lambda event=None: self.rename(callback), add="+")
        self.root.bind_all("<Escape>", self.destroy_rename_pop_up)

    def update_path_label(self, event=None):
        file_name = self.name_entry.get()
        if file_name.strip():
            self.ev3_path_label.configure(text=f"{self.ev3_path}/{file_name.strip()}")
        else:
            self.ev3_path_label.configure(text=f"{self.ev3_path}")

    def new_file(self, callback):
        content = self.name_entry.get().strip()
        if content:
            self.destroy_pop_up()
            callback(content)

    def compile(self, callback):
        output_file_name = self.compile_name_entry.get().strip()
        if output_file_name:
            self.destroy_compile_pop_up()
            callback(output_file_name)

    def confirm(self, callback):
        self.destroy_confirm_pop_up()
        callback()

    def rename(self, callback):
        new_path = self.name_entry.get().strip()
        if new_path:
            self.destroy_rename_pop_up()
            callback(self.old_ev3_path, new_path)

    def destroy_pop_up(self, event=None):
        self.root.unbind_all("<Escape>")
        self.overlay.destroy()

    def destroy_compile_pop_up(self, event=None):
        self.root.unbind_all("<Escape>")
        self.compile_overlay.destroy()

    def destroy_confirm_pop_up(self, event=None):
        self.root.unbind_all("<Escape>")
        self.confirm_overlay.destroy()

    def destroy_rename_pop_up(self, event=None):
        self.root.unbind_all("<Escape>")
        self.rename_overlay.destroy()