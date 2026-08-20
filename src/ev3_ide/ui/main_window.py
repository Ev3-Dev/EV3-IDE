import ctypes
from ctypes import wintypes

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QSplitter, QPushButton
from PySide6.QtCore import Qt, Signal

from ev3_ide.ui.widgets.toolbar import IDETitleBar
from ev3_ide.ui.widgets.left_sidebar import LeftSidebar
from ev3_ide.ui.widgets.editor_tabs import EditorTabs
from ev3_ide.ui.widgets.bottom_tabs import BottomTabs


WM_NCHITTEST = 0x0084
WM_NCCALCSIZE = 0x0083

HTCLIENT = 1
HTCAPTION = 2

HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", ctypes.c_void_p),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt_x", ctypes.c_long),
        ("pt_y", ctypes.c_long),
    ]

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]

class NCCALCSIZE_PARAMS(ctypes.Structure):
    _fields_ = [
        ("rgrc", RECT * 3),
        ("lppos", ctypes.c_void_p),
    ]


class MainWindow(QMainWindow):
    run_requested      = Signal()
    stop_requested     = Signal()
    upload_requested   = Signal()
    sync_requested     = Signal()
    file_open_requested = Signal(str)
    command_entered    = Signal(str)

    RESIZE_BORDER = 8

    def __init__(self, app, theme_manager):
        super().__init__()
        self.setObjectName("main_window")
        self.setMinimumSize(1200, 750)
        self.showMaximized()

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(5, 0, 5, 5)
        root.setSpacing(0)

        # Toolbar
        self.title_bar = IDETitleBar(self)
        self.title_bar.minimize_button.clicked.connect(self.showMinimized)
        self.title_bar.maximize_button.clicked.connect(lambda: (self.showNormal() if self.isMaximized() else self.showMaximized()))
        self.title_bar.close_button.clicked.connect(self.close)
        root.addWidget(self.title_bar)

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

    def nativeEvent(self, eventType, message):
        if eventType == "windows_generic_MSG":
            msg = MSG.from_address(message.__int__())

            if msg.message == WM_NCCALCSIZE and msg.wParam:

                params = NCCALCSIZE_PARAMS.from_address(
                    msg.lParam
                )

                rect = params.rgrc[0]

                print(
                    "NEW WINDOW:",
                    rect.left,
                    rect.top,
                    rect.right,
                    rect.bottom,
                )

                return True, 0

            elif msg.message == WM_NCHITTEST:
                x = ctypes.c_short(msg.lParam & 0xFFFF).value
                y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
                top_left = self.mapToGlobal(self.rect().topLeft())

                local_x = x - top_left.x()
                local_y = y - top_left.y()

                width = self.width()
                height = self.height()

                border = self.RESIZE_BORDER

                left = local_x < border
                right = local_x >= width - border

                top = local_y < border
                bottom = local_y >= height - border

                if top and left:
                    return True, HTTOPLEFT

                if top and right:
                    return True, HTTOPRIGHT

                if bottom and left:
                    return True, HTBOTTOMLEFT

                if bottom and right:
                    return True, HTBOTTOMRIGHT

                if left:
                    return True, HTLEFT

                if right:
                    return True, HTRIGHT

                if top:
                    return True, HTTOP

                if bottom:
                    return True, HTBOTTOM

                if 0 <= local_y < self.title_bar.height():
                    widget = self.childAt(local_x, local_y)
                    if isinstance(widget, QPushButton):
                        return False, HTCLIENT
                    return True, HTCAPTION

                return True, HTCLIENT

        return super().nativeEvent(eventType, message)

    # ── Öffentliche API – wird vom Controller aufgerufen ───────

    def open_file(self, path: str, content: str):
        self.editor_tabs.open_file(path, content)

    def log(self, text: str, kind: str = "output"):
        self.bottom_tabs.console.append_line(text, kind)

    def set_connected(self, host: str, conn_type: str):
        pass
        # self.toolbar.set_connected(host, conn_type)

    def set_disconnected(self):
        pass
        # self.toolbar.set_disconnected()

    def set_battery(self, percent: int):
        pass
        # self.toolbar.set_battery(percent)

    def update_display(self, raw: bytes):
        pass
        # self.right_sidebar.ev3_display.update_from_framebuffer(raw)

    def update_motor(self, port: str, speed: int):
        pass
        # self.right_sidebar.motor_widget.update_motor(port, speed)

    def update_sensor(self, port: str, name: str, value: str, bar: int = -1):
        pass
        # self.right_sidebar.sensor_widget.update_sensor(port, name, value, bar)

    def load_file_tree(self, tree: dict):
        self.left_sidebar.file_tree.load_tree(tree)