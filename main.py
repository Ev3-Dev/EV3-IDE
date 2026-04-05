import os
import sys
import ctypes
import customtkinter as ctk
from basic_gui import BasicGui
from ev3_handler import EV3Handler
from ssh_container import SSHContainer
from notification_manager import NotificationManager

# ---- Arbeitsverzeichnis setzen ----
if getattr(sys, 'frozen', False):
    # PyInstaller EXE
    os.chdir(sys._MEIPASS)
else:
    # Normaler Python-Run (z.B. PyCharm)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ---- Root-Fenster ----
root = ctk.CTk()

def load_font(font_path):
    FR_PRIVATE = 0x10
    ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)

load_font("fonts/JetBrainsMono-Regular.ttf")
load_font("fonts/Arial.ttf")
load_font("fonts/SegoeUI.ttf")

root.title("EV3-IDE")
root.iconbitmap("images/ev3.ico")
ctk.set_appearance_mode("dark")
root.minsize(1200, 700)
root.after(0, lambda: root.state("zoomed"))

ssh_container = SSHContainer()

notification_manager = NotificationManager()

gui = BasicGui(root, ssh_container, notification_manager)
ev3_handler = EV3Handler(gui, root, ssh_container, notification_manager)

gui.add_functions(ev3_handler)

ev3_handler.start_session()

gui.start_mainloop()