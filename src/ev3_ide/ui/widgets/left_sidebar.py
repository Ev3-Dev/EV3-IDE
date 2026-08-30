from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QStackedWidget, QFrame, QPushButton
from PySide6.QtCore import Signal

from ev3_ide.ui.widgets.files_widget import FilesWidget
from ev3_ide.ui.widgets.lib_manager import LibManager


class LeftSidebar(QFrame):
    item_clicked = Signal(dict)
    item_right_clicked = Signal(dict)
    back_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("left_sidebar")
        self.setMinimumWidth(250)

        # -------- Button-Leiste --------
        self.dropdown = QComboBox()
        self.dropdown.setObjectName("left_sidebar_dropdown")
        self.dropdown.addItems(["Files", "EV3 State", "Libraries"])
        self.dropdown.setFixedWidth(20)
        self.dropdown.setFixedWidth(110)

        # -------- Content-Area --------
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setContentsMargins(4, 4, 4, 4)
        self.buttons_layout.addWidget(self.dropdown)
        self.buttons_layout.addStretch()
        self.dynamic_buttons_layout = QHBoxLayout()
        self.buttons_layout.addLayout(self.dynamic_buttons_layout)

        self.files_widget = FilesWidget()
        self.ev3_view = QWidget()
        self.lib_manager = LibManager()

        page_container_layout = QHBoxLayout()
        page_container_layout.setContentsMargins(0, 0, 0, 0)

        self.page_container = QStackedWidget()
        self.page_container.setObjectName("left_sidebar_page_container")

        page_container_layout.addWidget(self.page_container)

        self.page_container.addWidget(self.files_widget)
        self.page_container.addWidget(self.ev3_view)
        self.page_container.addWidget(self.lib_manager)

        self.dropdown.currentIndexChanged.connect(self.index_changed)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addLayout(self.buttons_layout)
        main_layout.addLayout(page_container_layout)

        self.lib_manager.set_libs(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])

        self.index_changed(0)

        self.files_widget.item_clicked.connect(self.item_clicked)
        self.files_widget.item_right_clicked.connect(self.item_right_clicked)
        self.files_widget.back_requested.connect(self.back_requested)

    def update_directory(self, entries):
        self.files_widget.update_directory(entries)

    def clear_buttons_layout(self):
        while self.dynamic_buttons_layout.count():
            item = self.dynamic_buttons_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def fill_buttons_layout(self, widgets):
        for widget in widgets:
            self.dynamic_buttons_layout.addWidget(widget)

    def index_changed(self, index):
        self.clear_buttons_layout()
        if index == 0:
            self.fill_buttons_layout(self.files_widget.get_buttons_layout_widget())
        self.page_container.setCurrentIndex(index)
