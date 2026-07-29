from PySide6.QtWidgets import QFrame, QVBoxLayout, QListWidget, QPushButton, QLabel, QListWidgetItem, QWidget
from PySide6.QtCore import Signal, Qt

class LibManager(QWidget):
    install_requested = Signal(str)  # Lib-Name

    def __init__(self):
        super().__init__()
        self.setObjectName("lib_manager")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.lib_list = QListWidget()
        self.lib_list.viewport().setStyleSheet("background: transparent;")

        self.lib_list.setObjectName("lib_manager_list")

        layout.addWidget(self.lib_list)

        self.btn_install = QPushButton("Install")
        self.btn_install.setObjectName("btn_install")
        self.btn_install.clicked.connect(self._on_install)
        layout.addWidget(self.btn_install)

    def set_libs(self, libs: list[str]):
        self.lib_list.clear()
        for lib in libs:
            self.lib_list.addItem(QListWidgetItem(lib))

    def _on_install(self):
        print("Installing...")
        item = self.lib_list.currentItem()
        if item:
            self.install_requested.emit(item.text())