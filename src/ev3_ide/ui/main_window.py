import ctypes
from ctypes import wintypes
import posixpath

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QSplitter, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal, QPoint, QEvent, QTimer
from PySide6.QtGui import QShortcut, QKeySequence

from ev3_ide.ui.widgets.toolbar import IDETitleBar
from ev3_ide.ui.widgets.left_sidebar import LeftSidebar
from ev3_ide.ui.widgets.editor_tabs import EditorTabs
from ev3_ide.ui.widgets.bottom_tabs import BottomTabs

from ev3_ide.core.ev3_handler import EV3Handler


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

SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020


class MSG(ctypes.Structure):
    _fields_ = [("hwnd", ctypes.c_void_p), ("message", wintypes.UINT), ("wParam", wintypes.WPARAM), ("lParam", wintypes.LPARAM), ("time", wintypes.DWORD), ("pt_x", ctypes.c_long), ("pt_y", ctypes.c_long),]

class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG),]

class NCCALCSIZE_PARAMS(ctypes.Structure):
    _fields_ = [("rgrc", RECT * 3), ("lppos", ctypes.c_void_p),]


class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", RECT), ("rcWork", RECT), ("dwFlags", wintypes.DWORD),]


user32 = ctypes.windll.user32

MonitorFromWindow = user32.MonitorFromWindow
MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD,]
MonitorFromWindow.restype = wintypes.HMONITOR

GetMonitorInfoW = user32.GetMonitorInfoW
GetMonitorInfoW.argtypes = [wintypes.HMONITOR, ctypes.POINTER(MONITORINFO),]
GetMonitorInfoW.restype = wintypes.BOOL

MONITOR_DEFAULTTONEAREST = 2

SetWindowPos = user32.SetWindowPos
SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT,]
SetWindowPos.restype = wintypes.BOOL


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
        self.setMinimumSize(650, 450)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root_content = QVBoxLayout()
        root_content.setContentsMargins(5, 2, 5, 5)

        # Toolbar
        self.title_bar = IDETitleBar(self)
        self.title_bar.minimize_button.clicked.connect(self.showMinimized)
        self.title_bar.maximize_button.clicked.connect(self.toggle_maximized)
        self.title_bar.close_button.clicked.connect(self.close)
        root.addWidget(self.title_bar)

        root.addLayout(root_content)

        # Haupt-Splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setHandleWidth(5)
        main_splitter.splitterMoved.connect(lambda pos, index: self.update_splitter_handle(main_splitter))
        root_content.addWidget(main_splitter, stretch=1)

        # Linke Sidebar
        self.left_sidebar = LeftSidebar()
        main_splitter.addWidget(self.left_sidebar)

        # Mitte: Editor + Konsole
        center_splitter = QSplitter(Qt.Orientation.Vertical)
        center_splitter.setHandleWidth(5)
        center_splitter.splitterMoved.connect(lambda pos, index: self.update_splitter_handle(center_splitter))
        self.editor_tabs = EditorTabs()
        self.bottom_tabs = BottomTabs()
        self.bottom_tabs.command_entered.connect(self.command_entered)
        center_splitter.addWidget(self.editor_tabs)
        center_splitter.addWidget(self.bottom_tabs)
        center_splitter.setSizes([600, 200])
        main_splitter.addWidget(center_splitter)

        main_splitter.setSizes([100, 1200])

        self.showMaximized()

        # Widget-Signals
        self.ev3_handler = EV3Handler()
        self.ev3_handler.start_session()

        self.ev3_handler.ev3_connected.connect(lambda: self.title_bar.set_connection_state("• Connected"))
        self.ev3_handler.ev3_disconnected.connect(lambda: self.title_bar.set_connection_state("• Disconnected"))
        self.ev3_handler.directory_updated.connect(self.left_sidebar.update_directory)
        self.ev3_handler.file_loaded.connect(self.open_editor_tab)
        self.ev3_handler.file_written.connect(lambda path: print(path))
        self.ev3_handler.battery_updated.connect(self.title_bar.set_battery_state)
        self.ev3_handler.error.connect(self.handle_error)

        self.left_sidebar.item_clicked.connect(self.handle_left_clicked)
        self.left_sidebar.item_right_clicked.connect(self.handle_right_clicked)
        self.left_sidebar.back_requested.connect(self.handle_files_widget_back)
        self.left_sidebar.home_requested.connect(self.handle_files_home)
        self.left_sidebar.refresh_requested.connect(self.handle_files_refresh)

        # Shortcuts
        self.title_bar.save_requested.connect(self.save_current_file)

    # Shortcut-Funktionen
    def save_current_file(self):
        tab = self.editor_tabs.current_tab()
        if tab is None:
            return
        self.ev3_handler.save_file(tab.path, tab.editor.toPlainText())

    # Code-Editor-Logik
    def handle_left_clicked(self, data):
        if data["type"] == "file":
            if data["path"] in self.editor_tabs.get_opened_paths():
                self.editor_tabs.focus_tab(data["path"])
                return
            self.ev3_handler.get_file(data)
        else:
            self.ev3_handler.list_dir(data["path"])

    def handle_right_clicked(self, data):
        pass

    def open_editor_tab(self, data):
        self.editor_tabs.handle_file_content(data)

    def handle_files_widget_back(self):
        self.ev3_handler.go_back()

    def handle_files_home(self):
        self.ev3_handler.go_home()

    def handle_files_refresh(self):
        self.ev3_handler.refresh()

    def handle_error(self, data):
        print(f"Error: {data}")

    # MainWindow-Funktionen
    def update_splitter_handle(self, splitter):
        sizes = splitter.sizes()
        if 0 in sizes:
            splitter.setHandleWidth(0)
        else:
            splitter.setHandleWidth(5)

    def _refresh_button_state(self):
        button = self.title_bar.maximize_button
        button.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, False)
        button.update()

    def toggle_maximized(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self.update_maximize_icon()
        QTimer.singleShot(0, self._refresh_button_state)

    def update_maximize_icon(self):
        if self.isMaximized():
            self.title_bar.set_maximize_icon("window_restore")
        else:
            self.title_bar.set_maximize_icon("window_maximize")

    def _refresh_window_frame(self):
        hwnd = wintypes.HWND(int(self.winId()))
        SetWindowPos(hwnd, None, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED,)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.update_maximize_icon()
            QTimer.singleShot(0, self._refresh_window_frame)
        super().changeEvent(event)

    def nativeEvent(self, eventType, message):
        if eventType != "windows_generic_MSG":
            return super().nativeEvent(eventType, message)
        msg = MSG.from_address(message.__int__())

        # Title-Bar
        if msg.message == WM_NCCALCSIZE and msg.wParam:
            params = NCCALCSIZE_PARAMS.from_address(msg.lParam)
            rect = params.rgrc[0]
            if self.isMaximized():
                monitor = MonitorFromWindow(wintypes.HWND(int(self.winId())), MONITOR_DEFAULTTONEAREST,)
                info = MONITORINFO()
                info.cbSize = ctypes.sizeof(MONITORINFO)
                if GetMonitorInfoW(monitor, ctypes.byref(info)):
                    work = info.rcWork
                    rect.left = work.left
                    rect.top = work.top
                    rect.right = work.right
                    rect.bottom = work.bottom
            return True, 0

        # Resizing
        if msg.message == WM_NCHITTEST:
            global_x = ctypes.c_short(msg.lParam & 0xFFFF).value
            global_y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value

            local = self.mapFromGlobal(QPoint(global_x, global_y))

            x = local.x()
            y = local.y()

            width = self.width()
            height = self.height()

            border = self.RESIZE_BORDER

            if not self.isMaximized():
                left = x < border
                right = x >= width - border
                top = y < border
                bottom = y >= height - border
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

            if 0 <= y < self.title_bar.height():
                widget = self.childAt(x, y)
                if isinstance(widget, QPushButton) or isinstance(widget, QFrame):
                    return True, HTCLIENT
                return True, HTCAPTION
            return True, HTCLIENT

        return super().nativeEvent(eventType, message)

    def closeEvent(self, event):
        self.ev3_handler.stop()
        event.accept()