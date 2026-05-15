import customtkinter as ctk
from ev3_sender import EV3Sender
from PIL import Image
from pop_up_window import PopUpWindow
from context_pop_up import ContextPopUp

class DirectoryUpdater:
    def __init__(self, root, ssh_container, editor, console, run_button, save_button, device_label, device_found_label, notification_manager, register_layout_callback):
        # ------- Variablen --------
        self.root = root
        self.ssh_container = ssh_container
        self.ev3_sender = EV3Sender(ssh_container)
        self.editor = editor
        self.console = console
        self.pop_up_window = PopUpWindow(self.root)
        self.context_menu = ContextPopUp(self.root)
        self.notification_manager = notification_manager
        self.run_button = run_button
        self.save_button = save_button
        self.device_label = device_label
        self.device_found_label = device_found_label
        self.ev3_selected_path = "/home/robot"
        self.ev3_base_path = "/home/robot"
        self.ev3_run_path = ""
        self.base_frame_location_x = 5
        self.base_frame_location_y = 379
        self.ev3_screen_viewer_toggle_value = 1
        self.max_buttons = 22
        self.directory_buttons = []
        py_icon = ctk.CTkImage(light_image=Image.open("images/python.png"), dark_image=Image.open("images/python.png"), size=(13, 13))
        c_icon = ctk.CTkImage(light_image=Image.open("images/c.png"), dark_image=Image.open("images/c.png"), size=(12, 13))
        c_sharp_icon = ctk.CTkImage(light_image=Image.open("images/c-sharp.png"), dark_image=Image.open("images/c-sharp.png"), size=(13, 13))
        cpp_icon = ctk.CTkImage(light_image=Image.open("images/c++.png"), dark_image=Image.open("images/c++.png"), size=(13, 13))
        java_icon = ctk.CTkImage(light_image=Image.open("images/java.png"), dark_image=Image.open("images/java.png"), size=(13, 13))
        js_icon = ctk.CTkImage(light_image=Image.open("images/js.png"), dark_image=Image.open("images/js.png"), size=(13, 13))
        txt_icon = ctk.CTkImage(light_image=Image.open("images/text.png"), dark_image=Image.open("images/text.png"), size=(13, 13))
        dir_icon = ctk.CTkImage(light_image=Image.open("images/folder.png"), dark_image=Image.open("images/folder.png"), size=(13, 13))
        self.icon_map = {"py": py_icon, "c": c_icon, "cs": c_sharp_icon, "cpp": cpp_icon, "java": java_icon, "js": js_icon, "txt": txt_icon, "dir": dir_icon}
        self.default_icon = ctk.CTkImage(light_image=Image.open("images/text.png"), dark_image=Image.open("images/text.png"), size=(13, 13))
        # -------- GUI-Elemente --------
        self.directory_frame = ctk.CTkFrame(self.root, corner_radius=7, width=587, height=629, fg_color="#1C1A1A")
        self.directory_frame.place(x=self.base_frame_location_x, y=self.base_frame_location_y)
        self.item_frame = ctk.CTkScrollableFrame(self.directory_frame, height=550, width=543, corner_radius=7, fg_color="#151313", scrollbar_button_color="#2A2626", scrollbar_button_hover_color="#3B3333")
        self.item_frame.place(x=10, y=50)
        self.current_path_label = ctk.CTkLabel(self.item_frame, text=self.ev3_base_path, font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#151313")
        img = ctk.CTkImage(light_image=Image.open("images/back.png"), dark_image=Image.open("images/back.png"), size=(15, 15))
        self.back_button = ctk.CTkButton(self.directory_frame, text="Back", image=img, corner_radius=5, width=1, anchor="w", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#2A2626", bg_color="#1C1A1A", hover_color="#3B3333", command=self.go_back, border_color="#2A2626", border_width=1)
        self.back_button.place(x=11, y=11)
        img = ctk.CTkImage(light_image=Image.open("images/home.png"), dark_image=Image.open("images/home.png"), size=(15, 15))
        self.home_button = ctk.CTkButton(self.directory_frame, text="Home", image=img, corner_radius=5, width=1, anchor="w", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#2A2626", bg_color="#1C1A1A", hover_color="#3B3333", command=self.go_home, border_color="#2A2626", border_width=1)
        self.home_button.place(x=80, y=11)
        self.spacer_1 = ctk.CTkFrame(self.directory_frame, height=29, width=2, fg_color="#3B3333")
        self.spacer_1.place(x=155, y=11)
        img = ctk.CTkImage(light_image=Image.open("images/file.png"), dark_image=Image.open("images/file.png"), size=(15, 15))
        self.new_file_button = ctk.CTkButton(self.directory_frame, text="New file", image=img, corner_radius=5, width=1, anchor="w", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#2A2626", bg_color="#1C1A1A", hover_color="#3B3333", command=lambda: self.pop_up_window.create_overlay("New file", self.ev3_selected_path, self.new_file), border_color="#2A2626", border_width=1)
        self.new_file_button.place(x=164, y=11)
        img = ctk.CTkImage(light_image=Image.open("images/directory.png"), dark_image=Image.open("images/directory.png"), size=(15, 15))
        self.new_directory_button = ctk.CTkButton(self.directory_frame, text="New directory", image=img, corner_radius=5, width=1, anchor="w", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#2A2626", bg_color="#1C1A1A", hover_color="#3B3333", command=lambda: self.pop_up_window.create_overlay("New directory", self.ev3_selected_path, self.new_directory), border_color="#2A2626", border_width=1)
        self.new_directory_button.place(x=249, y=11)
        self.spacer_2 = ctk.CTkFrame(self.directory_frame, height=29, width=2, fg_color="#3B3333")
        self.spacer_2.place(x=366, y=11)
        img = ctk.CTkImage(light_image=Image.open("images/reload.png"), dark_image=Image.open("images/reload.png"), size=(15, 15))
        self.reload_button = ctk.CTkButton(self.directory_frame, text="Reload", image=img, corner_radius=5, width=1, anchor="w", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#2A2626", bg_color="#1C1A1A", hover_color="#3B3333", command=self.reload, border_color="#2A2626", border_width=1)
        self.reload_button.place(x=375, y=11)
        # Keybindings
        self.editor.editor.bind("<Shift-F8>", lambda event=None: self.run_program(self.editor.get_content()))
        self.editor.editor.bind("<Control-s>", lambda event=None: self.save_file())
        # Callback hinzufügen
        register_layout_callback(self.update_layout)

    def update_layout(self, width, height, is_console_hidden, is_status_panel_hidden, event=None):
        new_height = height - 379 - 5
        self.item_frame.configure(height=new_height-75)
        self.directory_frame.configure(height=new_height)

    def show_disconnected(self):
        # Eventuell löschen
        self.ev3_run_path = ""
        self.ssh_container.ssh = None
        self.root.after(100, self.delete_buttons)

    def is_file_selected(self):
        return bool(self.ev3_run_path)

    def save_file(self):
        self.editor.is_file_saved = True
        if not self.is_file_selected():
            return
        if self.ev3_selected_path.startswith("/home/robot/.EV3-IDE") or self.ev3_run_path.startswith("/home/robot/.EV3-IDE"):
            self.notification_manager.send_message(self.root, "Error", "Cannot edit EV3-IDE system files")
            return
        content = self.editor.get_content()
        content_bytes = content.encode("utf-8")
        length = len(content_bytes)
        self.ev3_sender.send_message(f"SAVE {self.ev3_run_path} {length}")
        self.ev3_sender.send_bytes(content_bytes)

    def reload(self):
        if self.ev3_selected_path:
            self.ev3_sender.send_message(f"LIST_DIRECTORY {self.ev3_selected_path}")

    def stop_ev3_program(self):
        self.ev3_sender.send_message("CANCEL_PROGRAM")

    def cancel_compilation(self):
        pass
        #self.ev3_sender.send_message("CANCEL_COMPILATION")

    def run_program(self, code, event=None):
        code = code.strip()
        if not code:
            return
        if self.is_file_selected():
            self.save_file()
            if self.ev3_run_path.endswith(".py"):
                self.console.delete_all()
                self.console.update_console(self.ev3_run_path + "\n\n")
                self.ev3_sender.send_message(f"RUN_FILE {self.ev3_run_path}")
                img = ctk.CTkImage(light_image=Image.open("images/stop.png"), dark_image=Image.open("images/stop.png"), size=(25, 25))
                self.run_button.configure(text="Stop", height=30, width=100, fg_color=["#C04848", "#C04848"], hover_color=["#8F3333", "#8F3333"], image=img, command=self.stop_ev3_program)
            elif self.ev3_run_path.endswith(".cpp"):
                # Pop-Up-Window-Logik mit Feld für Pfad der Zieldatei
                self.pop_up_window.create_compile_overlay(self.ev3_run_path, self.compile)
        else:
            if self.ssh_container.ssh is None:
                return
            self.console.delete_all()
            self.console.update_console("Temporary Execution\n\n")
            code_bytes = code.encode("utf-8")
            length = len(code_bytes)
            self.ev3_sender.send_message(f"RUN_TEMPORARY {length}")
            self.ev3_sender.send_bytes(code_bytes)
            img = ctk.CTkImage(light_image=Image.open("images/stop.png"), dark_image=Image.open("images/stop.png"), size=(25, 25))
            self.run_button.configure(text="Stop", height=30, width=100, fg_color=["#C04848", "#C04848"], hover_color=["#8F3333", "#8F3333"], image=img, command=self.stop_ev3_program)

    def new_file(self, file_name, event=None):
        if not file_name:
            self.notification_manager.show_message(self.root, "Error", "File name cannot be empty")
            return
        if " " in file_name:
            self.notification_manager.show_message(self.root, "Error", "File name cannot contain spaces")
            return
        if self.ev3_selected_path == "/home/robot/.EV3-IDE":
            self.notification_manager.show_message(self.root, "Error", "Cannot edit EV3-IDE system directory")
            return
        if "//" in file_name:
            self.notification_manager.show_message(self.root, "Error", "File name cannot contain '//'")
            return
        if ".." in file_name:
            self.notification_manager.show_message(self.root, "Error", "File name cannot contain '..'")
            return
        if file_name.endswith("/"):
            self.notification_manager.show_message(self.root, "Error", "File name cannot end with '/'")
            return
        self.ev3_sender.send_message(f"NEW_FILE {self.ev3_selected_path.rstrip('/')}/{file_name.lstrip('/')}")

    def new_directory(self, directory_name, event=None):
        if not directory_name:
            self.notification_manager.show_message(self.root, "Error", "Directory name cannot be empty")
            return
        if " " in directory_name:
            self.notification_manager.show_message(self.root, "Error", "Directory name cannot contain spaces")
            return
        if self.ev3_selected_path == "/home/robot/.EV3-IDE":
            self.notification_manager.show_message(self.root, "Error", "Cannot edit EV3-IDE system directory")
            return
        if "//" in directory_name:
            self.notification_manager.show_message(self.root, "Error", "Directory name cannot contain '//'")
            return
        if ".." in directory_name:
            self.notification_manager.show_message(self.root, "Error", "Directory name cannot contain '..'")
            return
        if directory_name.endswith("/"):
            self.notification_manager.show_message(self.root, "Error", "Directory name cannot end with '/'")
            return
        self.ev3_sender.send_message(f"NEW_DIRECTORY {self.ev3_selected_path.rstrip('/')}/{directory_name.lstrip('/')}")

    def compile(self, output_file_path, event=None):
        if not output_file_path:
            self.notification_manager.show_message(self.root, "Error", "Output file path cannot be empty")
            return
        if " " in output_file_path:
            self.notification_manager.show_message(self.root, "Error", "Output file path cannot contain spaces")
            return
        if "//" in output_file_path:
            self.notification_manager.show_message(self.root, "Error", "Output file path cannot contain '//'")
            return
        if ".." in output_file_path:
            self.notification_manager.show_message(self.root, "Error", "Output file path cannot contain '..'")
            return
        if output_file_path.endswith("/"):
            self.notification_manager.show_message(self.root, "Error", "Output file path cannot end with '/'")
            return
        self.ev3_sender.send_message(f"COMPILE {self.ev3_run_path} {output_file_path}")
        img = ctk.CTkImage(light_image=Image.open("images/close.png"), dark_image=Image.open("images/close.png"), size=(25, 25))
        self.run_button.configure(text="Cancel", fg_color=["#C04848", "#C04848"], hover_color=["#8F3333", "#8F3333"], command=self.cancel_compilation, height=30, width=120, image=img)
        self.console.delete_all()
        self.console.update_console(self.ev3_run_path + "\n\n")

    def delete_buttons(self):
        for btn in self.directory_buttons:
            btn.destroy()
        self.directory_buttons.clear()

    def button_action(self, file_type, path):
        if file_type == "dir":
            self.ev3_sender.send_message(f"LIST_DIRECTORY {path}")
        elif file_type == "file":
            self.ev3_sender.send_message(f"OPEN {path}")

    def delete_path(self, path):
        if path == "/home/robot/.EV3-IDE/ide_communication.py" or path == "/home/robot/.EV3-IDE/_temporary_run.py":
            self.notification_manager.show_message(self.root, "Error", "Cannot edit EV3-IDE system directory")
            return
        if path == "/home/robot/.EV3-IDE" or path == "/home/robot" or path == "/home" or path == "/" or path.endswith(".profile") or path.endswith(".bash_logout") or path.endswith(".bash_history") or path.endswith(".bashrc"):
            self.notification_manager.show_message(self.root, "Error", "Cannot edit system directory")
            return
        if path.strip() == self.ev3_run_path.strip() or self.ev3_run_path.strip().startswith(path.strip() + "/"):
            self.ev3_run_path = ""
            self.editor.editor.delete("1.0", "end")
            self.program_finished()
            self.editor.syntax_highlighting = ".py"
            self.console.delete_all()
            self.console.update_console("Select a file")
        self.ev3_selected_path = "/home/robot"
        self.ev3_sender.send_message(f"DELETE {path}")

    def rename_path(self, old_path, new_path):
        if old_path == "/home/robot/.EV3-IDE/ide_communication.py" or old_path == "/home/robot/.EV3-IDE/_temporary_run.py" or old_path == "/home/robot/.EV3-IDE":
            self.notification_manager.show_message(self.root, "Error", "Cannot edit EV3-IDE system directory")
            return
        if old_path == "/home/robot" or old_path == "/home" or old_path == "/" or old_path.endswith(".profile") or old_path.endswith(".bash_logout") or old_path.endswith(".bash_history") or old_path.endswith(".bashrc"):
            self.notification_manager.show_message(self.root, "Error", "Cannot edit system directory")
            return
        if not old_path.startswith("/home/robot"):
            self.notification_manager.show_message(self.root, "Error", "Cannot edit system directory")
            return
        if not new_path:
            self.notification_manager.show_message(self.root, "Error", "New path cannot be empty")
            return
        if " " in new_path:
            self.notification_manager.show_message(self.root, "Error", "New path cannot contain spaces")
            return
        if "//" in new_path:
            self.notification_manager.show_message(self.root, "Error", "New path cannot contain '//'")
            return
        if ".." in new_path:
            self.notification_manager.show_message(self.root, "Error", "New path cannot contain '..'")
            return
        if new_path.endswith("/"):
            self.notification_manager.show_message(self.root, "Error", "New path cannot end with '/'")
            return
        if not new_path.startswith("/home/robot"):
            self.notification_manager.show_message(self.root, "Error", "Cannot edit system directory")
            return
        if old_path.strip() == self.ev3_run_path.strip() or self.ev3_run_path.strip().startswith(old_path.strip() + "/"):
            self.ev3_run_path = ""
            self.editor.editor.delete("1.0", "end")
            self.program_finished()
            self.editor.syntax_highlighting = ".py"
            self.console.delete_all()
            self.console.update_console("Select a file")
        self.ev3_selected_path = "/home/robot"
        self.ev3_sender.send_message(f"RENAME {old_path} {new_path}")

    def context_open(self, entry_type, path):
        self.button_action(entry_type, path)

    def context_rename(self, entry_type, path):
        self.pop_up_window.create_rename_overlay(path, self.rename_path)

    def context_delete(self, entry_type, path):
        # Sicherheitswarnung
        self.pop_up_window.create_confirm_overlay(path, lambda: self.delete_path(path))

    def context_execute(self, entry_type, path):
        self.editor.editor.delete("1.0", "end")
        self.console.delete_all()
        self.console.update_console("Select a file\n\n")
        self.ev3_run_path = ""
        self.ev3_sender.send_message(f"EXECUTE {path}")

    def update_directory(self, content):
        self.delete_buttons()
        self.ev3_selected_path = content["path"]
        self.current_path_label.configure(text=self.ev3_selected_path)
        entries = content["entries"]
        self.current_path_label.pack()
        for index, entry in enumerate(entries):
            entry_name = entry["name"]
            entry_type = entry["type"]
            file_ext = entry_name.split(".")[-1] if entry_type != "dir" else "dir"
            icon = self.icon_map.get(file_ext, self.default_icon)
            full_path = self.ev3_selected_path + "/" + entry_name
            button = ctk.CTkButton(self.item_frame, text=f"{entry_name}", image=icon, compound="left", corner_radius=5, width=523, anchor="w", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#151313", bg_color="#151313", command=lambda t=entry_type, n=entry_name: self.button_action(t, self.ev3_selected_path + "/" + n))
            button.bind("<Button-3>", lambda event, p=full_path, t=entry_type: self.context_menu.show_context_menu(event, p, t, self.context_open, self.context_rename, self.context_delete, self.context_execute))
            button.pack()
            self.directory_buttons.append(button)
        # ---- Test: Automatisches Aktualisieren der Scrollbar ----
        self.item_frame._parent_canvas.update_idletasks()
        self.item_frame._parent_canvas.config(scrollregion=self.item_frame._parent_canvas.bbox("all"))
        self.item_frame._parent_canvas.yview_moveto(0)

    def open_file(self, file_content):
        if not self.editor.is_file_saved:
            self.save_file()
        if "error" in file_content or "content" not in file_content:
            return
        self.ev3_run_path = file_content["path"]
        # Button-Beschriftung anpassen
        if self.ev3_run_path.endswith(".cpp"):
            img = ctk.CTkImage(light_image=Image.open("images/compile.png"), dark_image=Image.open("images/compile.png"), size=(25, 25))
            self.run_button.configure(text="Compile", fg_color=["#3B8ED0","#1F6AA5"], hover_color=["#36719F", "#144870"], height=30, width=120, image=img)
            self.save_button.place(x=132, y=5)
            self.device_label.place(x=250, y=7)
            self.device_found_label.place(x=305, y=7)
        else:
            img = ctk.CTkImage(light_image=Image.open("images/play.png"), dark_image=Image.open("images/play.png"), size=(25, 25))
            self.run_button.configure(text="Run", fg_color=["#3B8ED0","#1F6AA5"], hover_color=["#36719F", "#144870"], height=30, width=100, image=img)
            self.save_button.place(x=112, y=5)
            self.device_label.place(x=230, y=7)
            self.device_found_label.place(x=285, y=7)
        index = file_content["path"].rfind(".")
        if index != -1:
            highlighting_type = file_content["path"][index:]
            self.editor.syntax_highlighting = highlighting_type
        self.editor.editor.delete("1.0", "end")
        self.editor.editor.insert("1.0", file_content["content"])
        self.editor.highlight_syntax(None)
        self.console.delete_all()
        self.console.update_console(self.ev3_run_path + "\n\n")

    def go_back(self):
        if not self.ev3_selected_path:
            return
        if self.ev3_selected_path == "/home/robot" or self.ev3_selected_path == "/home" or self.ev3_selected_path == "/":
            return
        index = self.ev3_selected_path.rfind("/")
        if index != -1:
            new_directory = self.ev3_selected_path[:index]
            self.ev3_sender.send_message(f"LIST_DIRECTORY {new_directory}")

    def go_home(self):
        self.ev3_sender.send_message(f"LIST_DIRECTORY {self.ev3_base_path}")

    def toggle_ev3_screen_viewer(self, value):
        self.ev3_screen_viewer_toggle_value = value
        self.ev3_sender.send_message(f"SCREEN_VIEWER {value}")

    def program_finished(self):
        self.console.program_finished()
        # Sicher keinen Code angeben, da sichergestellt ist, dass eine Python-Datei schon offen war und keine temporäre Datei angelegt werden muss
        img = ctk.CTkImage(light_image=Image.open("images/play.png"), dark_image=Image.open("images/play.png"), size=(25, 25))
        self.run_button.configure(text="Run", height=30, width=100, fg_color=["#3B8ED0","#1F6AA5"], hover_color=["#36719F", "#144870"], image=img, command=lambda: self.run_program(self.editor.get_content()))
        self.save_button.place(x=112, y=5)
        self.device_label.place(x=230, y=7)
        self.device_found_label.place(x=285, y=7)

    def compilation_finished(self):
        img = ctk.CTkImage(light_image=Image.open("images/compile.png"), dark_image=Image.open("images/compile.png"), size=(25, 25))
        self.run_button.configure(text="Compile", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"], command=lambda: self.run_program(self.editor.get_content()), height=30, width=120, image=img)

    def hide_all_elements(self):
        self.directory_frame.place_forget()

    def show_all_elements(self):
        self.directory_frame.place(x=self.base_frame_location_x, y=self.base_frame_location_y)