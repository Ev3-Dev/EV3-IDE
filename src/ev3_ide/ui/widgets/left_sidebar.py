from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QStackedWidget, QFrame
from PySide6.QtCore import Signal

from ev3_ide.ui.widgets.files_widget import FilesWidget
from ev3_ide.ui.widgets.lib_manager import LibManager


class LeftSidebar(QFrame):
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
        self.files_widget = FilesWidget()
        self.ev3_view = QWidget()
        self.lib_manager = LibManager()

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(4, 4, 4, 4)
        buttons_layout.addWidget(self.dropdown)
        buttons_layout.addStretch()

        page_container_layout = QHBoxLayout()
        page_container_layout.setContentsMargins(0, 0, 0, 0)

        self.page_container = QStackedWidget()
        self.page_container.setObjectName("left_sidebar_page_container")

        page_container_layout.addWidget(self.page_container)

        self.page_container.addWidget(self.files_widget)
        self.page_container.addWidget(self.ev3_view)
        self.page_container.addWidget(self.lib_manager)

        self.dropdown.currentIndexChanged.connect(self.page_container.setCurrentIndex)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(page_container_layout)

        self.lib_manager.set_libs(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])

    def update_directory(self, message):
        self.files_widget.update_directory(message)