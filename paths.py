import os
import sys

if getattr(sys, 'frozen', False):
    # EXE: Bilder und Tools liegen direkt im temporären MEIPASS
    IMAGES = os.path.join(sys._MEIPASS, "images")
    TOOLS  = os.path.join(sys._MEIPASS, "tools")
else:
    # Normaler Python-Run: src/ ist BASE_PATH
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_PATH, ".."))
    IMAGES = os.path.join(PROJECT_ROOT, "images")
    TOOLS  = os.path.join(PROJECT_ROOT, "tools")