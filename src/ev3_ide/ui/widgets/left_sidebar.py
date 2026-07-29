from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QStackedWidget, QFrame
from ev3_ide.ui.widgets.file_tree import FileTree
from ev3_ide.ui.widgets.lib_manager import LibManager

class LeftSidebar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("left_sidebar")
        self.setMinimumWidth(250)

        # -------- Button-Leiste --------
        self.dropdown = QComboBox(self)
        self.dropdown.setObjectName("left_sidebar_dropdown")
        self.dropdown.addItems(["Files", "EV3 State", "Libraries"])
        self.dropdown.setFixedWidth(20)
        self.dropdown.setFixedWidth(110)
        self.dropdown.move(3, 3)

        # -------- Content-Area --------
        self.file_tree = FileTree()
        self.ev3_view = QWidget()
        self.lib_manager = LibManager()

        # Beispiel
        self.file_tree.load_tree({"main.py": "file", "scripts": {"fnndkssfnn": "file"}}, "/home/robot")
        self.lib_manager.set_libs(["ev3dev2", "ev3dev.h", "ev3dev.cpp"])

        page_container_layout = QHBoxLayout(self)
        page_container_layout.setContentsMargins(10, 40, 10, 10)

        self.page_container = QStackedWidget(self)
        self.page_container.setObjectName("left_sidebar_page_container")

        page_container_layout.addWidget(self.page_container)

        self.page_container.addWidget(self.file_tree)
        self.page_container.addWidget(self.ev3_view)
        self.page_container.addWidget(self.lib_manager)

        self.dropdown.currentIndexChanged.connect(self.page_container.setCurrentIndex)