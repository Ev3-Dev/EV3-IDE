from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from ev3_ide.core.resources import resource_path



class IDETitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(40)

        self.ev3_state = "Disconnected"

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 0, 0, 0)
        main_layout.setSpacing(5)

        ev3_layout = QHBoxLayout()
        ev3_layout.setContentsMargins(0, 0, 0, 0)
        ev3_layout.setSpacing(5)

        windows_buttons_layout = QHBoxLayout()
        windows_buttons_layout.setContentsMargins(0, 0, 0, 0)
        windows_buttons_layout.setSpacing(0)

        self.maximize_icon = QIcon(resource_path("ui/icons/window_maximize.svg"))
        self.restore_icon = QIcon(resource_path("ui/icons/window_restore.svg"))

        # Toolbar
        self.logo = QLabel("EV3")

        self.run_button = QPushButton("Run")
        self.run_button.setObjectName("run_button")
        self.run_button.setFixedSize(90, 30)

        # EV3-Layout
        self.ev3_connection_label = QLabel("• Disconnected")
        self.ev3_connection_label.setObjectName("ev3_connection_label")

        self.ev3_battery_label = QLabel("Battery: -")
        self.ev3_battery_label.setObjectName("ev3_battery_label")

        ev3_layout.addWidget(self.ev3_connection_label)
        ev3_layout.addWidget(self.ev3_battery_label)

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

        windows_buttons_layout.addWidget(self.minimize_button)
        windows_buttons_layout.addWidget(self.maximize_button)
        windows_buttons_layout.addWidget(self.close_button)

        main_layout.addWidget(self.logo)
        main_layout.addWidget(self.run_button)
        main_layout.addStretch()
        main_layout.addLayout(ev3_layout)
        main_layout.addStretch()
        main_layout.addLayout(windows_buttons_layout)

    def set_connection_state(self, state):
        if state != self.ev3_state:
            self.ev3_state = state
            self.ev3_connection_label.setText(state)

    def set_battery_state(self, data):
        state = data["voltage_now"]
        print(f"Battery updated: {state}")
        self.ev3_battery_label.setText(f"Battery: {state}")

    def set_maximize_icon(self, icon_name):
        self.maximize_button.setIcon(QIcon(resource_path(f"ui/icons/{icon_name}.svg")))