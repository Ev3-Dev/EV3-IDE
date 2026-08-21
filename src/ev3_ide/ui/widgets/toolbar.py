from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from ev3_ide.core.resources import resource_path



class IDETitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 0, 0)
        layout.setSpacing(0)

        self.maximize_icon = QIcon(resource_path("ui/icons/window_maximize.svg"))
        self.restore_icon = QIcon(resource_path("ui/icons/window_restore.svg"))

        # Toolbar
        self.logo = QLabel("EV3")

        self.run_button = QPushButton("Run")

        # Windows-Buttons
        self.minimize_button = QPushButton()
        self.minimize_button.setObjectName("minimize_button")
        self.minimize_button.setFixedSize(48, 40)
        self.minimize_button.setIcon(QIcon(resource_path("ui/icons/window_minimize.svg")))
        self.minimize_button.setIconSize(QSize(18, 18))

        self.maximize_button = QPushButton()
        self.maximize_button.setObjectName("maximize_button")
        self.maximize_button.setFixedSize(48, 40)
        self.maximize_button.setIcon(self.restore_icon)
        self.maximize_button.setIconSize(QSize(18, 18))

        self.close_button = QPushButton()
        self.close_button.setObjectName("close_button")
        self.close_button.setFixedSize(48, 40)
        self.close_button.setIcon(QIcon(resource_path("ui/icons/window_close.svg")))
        self.close_button.setIconSize(QSize(18, 18))

        layout.addWidget(self.logo)
        layout.addWidget(self.run_button)
        layout.addStretch()
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)

    def set_maximize_icon(self, icon_name):
        self.maximize_button.setIcon(QIcon(resource_path(f"ui/icons/{icon_name}.svg")))