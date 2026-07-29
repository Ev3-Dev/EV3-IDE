from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt, Signal
from ev3_ide.ui.widgets.toolbar import Toolbar
from ev3_ide.ui.widgets.left_sidebar import LeftSidebar
from ev3_ide.ui.widgets.editor_tabs import EditorTabs
from ev3_ide.ui.widgets.bottom_tabs import BottomTabs

class MainWindow(QMainWindow):
    # Signals nach außen – verbindet UI mit Logik
    run_requested      = Signal()
    stop_requested     = Signal()
    upload_requested   = Signal()
    sync_requested     = Signal()
    file_open_requested = Signal(str)
    command_entered    = Signal(str)

    def __init__(self, app, theme_manager):
        super().__init__()
        self.setObjectName("main_window")
        self.setWindowTitle("EV3 Studio")
        self.setMinimumSize(1200, 750)
        self.showMaximized()

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(5, 5, 5, 5)
        root.setSpacing(0)

        # Toolbar
        self.toolbar = Toolbar()
        self.toolbar.run_clicked.connect(self.run_requested)
        self.toolbar.stop_clicked.connect(self.stop_requested)
        self.toolbar.upload_clicked.connect(self.upload_requested)
        self.toolbar.sync_clicked.connect(self.sync_requested)
        root.addWidget(self.toolbar)

        # Haupt-Splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(main_splitter, stretch=1)

        # Linke Sidebar
        self.left_sidebar = LeftSidebar()
        self.left_sidebar.file_tree.file_opened.connect(self.file_open_requested)
        main_splitter.addWidget(self.left_sidebar)

        # Mitte: Editor + Konsole
        center_splitter = QSplitter(Qt.Orientation.Vertical)
        self.editor_tabs = EditorTabs()
        self.bottom_tabs = BottomTabs()
        self.bottom_tabs.command_entered.connect(self.command_entered)
        center_splitter.addWidget(self.editor_tabs)
        center_splitter.addWidget(self.bottom_tabs)
        center_splitter.setSizes([600, 200])
        main_splitter.addWidget(center_splitter)

        main_splitter.setSizes([150, 850])
        main_splitter.setCollapsible(0, False)

        self.editor_tabs.open_file("/home/robot/projekt/main.py", "")
        self.editor_tabs.open_file("/home/robot/projekt/fahrsteuerung.py","")

    # ── Öffentliche API – wird vom Controller aufgerufen ──────────

    def open_file(self, path: str, content: str):
        self.editor_tabs.open_file(path, content)

    def log(self, text: str, kind: str = "output"):
        self.bottom_tabs.console.append_line(text, kind)

    def set_connected(self, host: str, conn_type: str):
        self.toolbar.set_connected(host, conn_type)

    def set_disconnected(self):
        self.toolbar.set_disconnected()

    def set_battery(self, percent: int):
        self.toolbar.set_battery(percent)

    def update_display(self, raw: bytes):
        self.right_sidebar.ev3_display.update_from_framebuffer(raw)

    def update_motor(self, port: str, speed: int):
        self.right_sidebar.motor_widget.update_motor(port, speed)

    def update_sensor(self, port: str, name: str, value: str, bar: int = -1):
        self.right_sidebar.sensor_widget.update_sensor(port, name, value, bar)

    def load_file_tree(self, tree: dict):
        self.left_sidebar.file_tree.load_tree(tree)