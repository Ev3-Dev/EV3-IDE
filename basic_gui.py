import customtkinter as ctk
from PIL import Image
from editor import Editor
from status_updater import StatusUpdater
from directory_updater import DirectoryUpdater
from console import Console
from settings import Settings

class BasicGui:
    def __init__(self, root, ssh_container, notification_manager):
        # -------- Variablen, die vor den Instanzen existieren müssen --------
        self.layout_callbacks = []
        self.last_width = 0
        self.last_height = 0
        self._resize_pending = False
        self.CONSOLE_HEIGHT = 260
        # Klassen-Instanzen
        self.root = root
        self.ssh_container = ssh_container
        self.root.update()
        self.editor = Editor(self.root, self.ssh_container, self.register_layout_callback, self.CONSOLE_HEIGHT)
        self.console = Console(self.root, self.CONSOLE_HEIGHT, self.register_layout_callback)
        self.status_updater = StatusUpdater(self.root, self.ssh_container)
        self.notification_manager = notification_manager
        self.settings = Settings(self.root)
        # -------- Variablen ---------
        self.is_console_hidden = False
        self.is_status_panel_hidden = False
        self.is_connected = False
        self.ev3_screen_viewer_toggle_value = 1
        self.syntax_highlighting_enabled = True
        # -------- GUI-Elemente --------
        # ++++++++ Top-Leiste ++++++++
        img = ctk.CTkImage(light_image=Image.open("images/play.png"), dark_image=Image.open("images/play.png"), size=(25, 25))
        self.run_button = ctk.CTkButton(self.root, text="Run", font=("Segoe UI", 15, "bold"), corner_radius=7, width=100, height=33, image=img, text_color="#191919", command=lambda: self.directory_updater.run_program(self.editor.get_content()))
        self.run_button.place(x=5, y=5)
        img = ctk.CTkImage(light_image=Image.open("images/download.png"), dark_image=Image.open("images/download.png"), size=(25, 25))
        self.save_button = ctk.CTkButton(self.root, text="Save", font=("Segoe UI", 15, "bold"), corner_radius=7, width=100, height=33, image=img, text_color="#191919", command=self.save_file)
        self.save_button.place(x=112, y=5)
        self.device_label = ctk.CTkLabel(self.root, text="Device:", font=("Segoe UI", 15), text_color="#D4D4D4")
        self.device_label.place(x=230, y=7)
        self.device_found_label = ctk.CTkLabel(self.root, text="• None", font=("Segoe UI", 15, "bold"), text_color="#FF6B6B")
        self.device_found_label.place(x=285, y=7)
        img = ctk.CTkImage(light_image=Image.open("images/setting.png"), dark_image=Image.open("images/setting.png"), size=(25, 25))
        self.settings_button = ctk.CTkButton(self.root, text="", font=("Segoe UI", 15, "bold"), image=img, height=1, width=1, corner_radius=7, fg_color="#1C1A1A", bg_color="#1C1A1A", border_width=2, border_color="black", command=lambda: self.settings.open_settings(self.toggle_ev3_screen_viewer, self.ev3_screen_viewer_toggle_value, self.toggle_syntax_highlighting), hover_color="gray")
        self.settings_button.place(relx=1.0, x=-85, y=5, anchor="ne")
        img = ctk.CTkImage(light_image=Image.open("images/computer.png"), dark_image=Image.open("images/computer.png"), size=(25, 25))
        self.hide_status_panel_button = ctk.CTkButton(self.root, text="", font=("Segoe UI", 15, "bold"), image=img, height=1, width=1, corner_radius=7, fg_color="#1C1A1A", bg_color="#1C1A1A", border_width=2, border_color="black", command=self.hide_status_panel, hover_color="gray")
        self.hide_status_panel_button.place(relx=1.0, x=-45, y=5, anchor="ne")
        img = ctk.CTkImage(light_image=Image.open("images/code.png"), dark_image=Image.open("images/code.png"), size=(25, 25))
        self.hide_console_button = ctk.CTkButton(self.root, text="", font=("Segoe UI", 15, "bold"), image=img, height=1, width=1, corner_radius=7, fg_color="#1C1A1A", bg_color="#1C1A1A", border_width=2, border_color="black", command=self.hide_console, hover_color="gray")
        self.hide_console_button.place(relx=1.0, x=-5, y=5, anchor="ne")
        # Directory-Updater-Instanz
        self.directory_updater = DirectoryUpdater(self.root, self.ssh_container, self.editor, self.console, self.run_button, self.save_button, self.device_label, self.device_found_label, self.notification_manager, self.register_layout_callback)
        # Disconnected-Funktionsaufruf
        self.device_disconnected(show_notification=False)
        # Keybindings
        self.root.bind("<Configure>", self.update_layout)

    def register_layout_callback(self, callback):
        self.layout_callbacks.append(callback)

    def update_layout(self, event=None):
        if self._resize_pending:
            return
        self._resize_pending = True
        self.root.after(16, self._do_update_layout)

    def _do_update_layout(self, event=None):
        new_width = self.root.winfo_width()
        new_height = self.root.winfo_height()
        if (new_width == self.last_width) and (new_height == self.last_height):
            self._resize_pending = False
            return
        for callback in self.layout_callbacks:
            callback(new_width, new_height, self.is_console_hidden, self.is_status_panel_hidden, event)
        self.last_width = new_width
        self.last_height = new_height
        self._resize_pending = False

    def add_functions(self, ev3_handler):
        self.ev3_handler = ev3_handler

    def device_connected(self, device_name):
        self.is_connected = True
        self.notification_manager.show_message(self.root, "Info", f"Connected to '{device_name}'\nStarting processes...")
        self.device_found_label.configure(text=f"{device_name}", text_color="#7BB342")
        self.status_updater.show_connected(device_name)

    def device_disconnected(self, show_notification=True):
        if show_notification and self.is_connected:
            self.is_connected = False
            self.notification_manager.show_message(self.root, "Error", "Lost connection to EV3")
            self.root.after(1000, self.ev3_handler.reconnect)
        self.device_found_label.configure(text="• None", text_color="#FF6B6B")
        self.status_updater.show_disconnected()
        self.directory_updater.show_disconnected()

    def hide_console(self):
        self.is_console_hidden = True
        self.console.console.place_forget()
        self.editor.update_layout(self.root.winfo_width(), self.root.winfo_height(), self.is_console_hidden, self.is_status_panel_hidden)
        self.hide_console_button.configure(command=self.show_console)

    def show_console(self):
        self.is_console_hidden = False
        if not self.is_status_panel_hidden:
            self.console.console.place(x=596, y=self.root.winfo_height()-5, anchor="sw")
        else:
            self.console.console.place(x=5, y=self.root.winfo_height()-5, anchor="sw")
        self.console.update_layout(self.root.winfo_width(), self.root.winfo_height(), self.is_console_hidden, self.is_status_panel_hidden)
        self.editor.update_layout(self.root.winfo_width(), self.root.winfo_height(), self.is_console_hidden, self.is_status_panel_hidden)
        self.hide_console_button.configure(command=self.hide_console)

    def hide_status_panel(self):
        self.is_status_panel_hidden = True
        self.status_updater.hide_all_elements()
        self.directory_updater.hide_all_elements()
        self.editor.update_layout(self.root.winfo_width(), self.root.winfo_height(), self.is_console_hidden, self.is_status_panel_hidden)
        self.editor.place_editor(x=5, y=80)
        if not self.is_console_hidden:
            self.console.console.place(x=5, y=self.root.winfo_height()-5, anchor="sw")
        self.console.update_layout(self.root.winfo_width(), self.root.winfo_height(), self.is_console_hidden, self.is_status_panel_hidden)
        self.hide_status_panel_button.configure(command=self.show_status_panel)

    def show_status_panel(self):
        self.is_status_panel_hidden = False
        self.status_updater.show_all_elements()
        self.directory_updater.show_all_elements()
        self.editor.update_layout(self.root.winfo_width(), self.root.winfo_height(), self.is_console_hidden, self.is_status_panel_hidden)
        self.editor.place_editor(x=596, y=80)
        if not self.is_console_hidden:
            self.console.console.place(x=596, y=self.root.winfo_height()-5, anchor="sw")
        self.console.update_layout(self.root.winfo_width(), self.root.winfo_height(), self.is_console_hidden, self.is_status_panel_hidden)
        self.hide_status_panel_button.configure(command=self.hide_status_panel)

    # -------
    # Status-Updates
    # --------
    def update_screen(self, content):
        self.status_updater.update_screen(content)
    def update_battery(self, voltage_now, voltage_min, voltage_max):
        self.status_updater.update_battery(voltage_now, voltage_min, voltage_max)
    def update_motors(self, motor_dict):
        self.status_updater.update_motors(motor_dict)
    def update_sensors(self, sensor_dict):
        self.status_updater.update_sensors(sensor_dict)

    # --------
    # Directory-Updates
    # --------
    def update_directory(self, content):
        self.directory_updater.update_directory(content)
    def open_file(self, file_content):
        self.directory_updater.open_file(file_content)
    def save_file(self):
        self.directory_updater.save_file()
    def update_console(self, content):
        self.console.update_console(content)
    def update_console_std(self, std_type, content):
        self.console.update_console_std(std_type, content)
    def ev3_program_finished(self):
        self.directory_updater.program_finished()
    def compilation_finished(self):
        self.directory_updater.compilation_finished()
    def toggle_ev3_screen_viewer(self, value):
        self.ev3_screen_viewer_toggle_value = value
        self.directory_updater.toggle_ev3_screen_viewer(value)
        self.settings_button.configure(command=lambda: self.settings.open_settings(self.toggle_ev3_screen_viewer, self.ev3_screen_viewer_toggle_value, self.toggle_syntax_highlighting))
    def toggle_syntax_highlighting(self, value):
        self.syntax_highlighting_enabled = value
        self.editor.syntax_highlighting_enabled = value
        self.editor.highlight_syntax()

    def start_mainloop(self):
        self.root.mainloop()