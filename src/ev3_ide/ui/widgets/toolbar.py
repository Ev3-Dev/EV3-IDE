from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, QSize, QEvent, QObject, Signal
from PySide6.QtGui import QIcon, QKeySequence, QShortcut

from ev3_ide.core.resources import resource_path
from ev3_ide.ui.widgets.battery_popup import BatteryPopup


class IDETitleBar(QWidget):
    run_requested = Signal()
    save_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(40)

        self.ev3_state = "Disconnected"
        self.previous_battery_percentage = 0
        self.battery_info = {}

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 0, 0, 0)
        main_layout.setSpacing(10)

        self.ev3_frame = QFrame()
        self.ev3_frame.setObjectName("ev3_frame")
        self.ev3_frame.setFixedHeight(30)

        self.battery_popup = BatteryPopup(self.ev3_frame)

        ev3_layout = QHBoxLayout(self.ev3_frame)
        ev3_layout.setContentsMargins(8, 0, 8, 0)
        ev3_layout.setSpacing(10)

        ev3_battery_layout = QHBoxLayout()
        ev3_battery_layout.setContentsMargins(0, 0, 0, 0)
        ev3_battery_layout.setSpacing(2)

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
        self.run_button.setIconSize(QSize(18, 18))
        self.run_button.setIcon(QIcon(resource_path("ui/icons/run.svg")))

        self.save_button = QPushButton(" Save")
        self.save_button.setObjectName("save_button")
        self.save_button.setFixedSize(90, 30)
        self.save_button.setIconSize(QSize(17, 17))
        self.save_button.setIcon(QIcon(resource_path("ui/icons/save.svg")))

        toolbar_buttons_layout = QHBoxLayout()
        toolbar_buttons_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_buttons_layout.setSpacing(5)
        toolbar_buttons_layout.addWidget(self.run_button)
        toolbar_buttons_layout.addWidget(self.save_button)

        # EV3-Layout
        self.ev3_connection_label = QLabel("• Disconnected")
        self.ev3_connection_label.setObjectName("ev3_connection_label")

        self.ev3_battery_icon_label = QLabel()
        self.ev3_battery_icon_label.setPixmap(QIcon(resource_path("ui/icons/battery-20.svg")).pixmap(QSize(14, 14)))

        self.ev3_battery_label = QLabel("–")
        self.ev3_battery_label.setObjectName("ev3_battery_label")

        ev3_battery_layout.addWidget(self.ev3_battery_icon_label)
        ev3_battery_layout.addWidget(self.ev3_battery_label)

        ev3_layout.addWidget(self.ev3_connection_label)
        ev3_layout.addLayout(ev3_battery_layout)

        # Help-Button
        self.ev3_help_button = QPushButton("?")
        self.ev3_help_button.setObjectName("ev3_help_button")
        self.ev3_help_button.setFixedSize(30, 30)

        ev3_right_layout = QHBoxLayout()
        ev3_right_layout.setContentsMargins(0, 0, 0, 0)
        ev3_right_layout.setSpacing(5)

        ev3_right_layout.addWidget(self.ev3_frame)
        ev3_right_layout.addWidget(self.ev3_help_button)

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
        main_layout.addLayout(toolbar_buttons_layout)
        main_layout.addStretch(stretch=75)
        main_layout.addLayout(ev3_right_layout)
        main_layout.addStretch(stretch=1)
        main_layout.addLayout(windows_buttons_layout)

        self.ev3_frame.installEventFilter(self)

        # Shortcuts
        self.run_button.clicked.connect(self.run_requested)
        self.save_action = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_action.activated.connect(self.save_requested)
        self.save_button.clicked.connect(self.save_requested)

        self.run_button.setEnabled(False)
        self.save_button.setEnabled(False)

    def set_connection_state(self, state):
        if state != self.ev3_state:
            self.ev3_state = state
            self.ev3_connection_label.setText(state)
            self.ev3_battery_label.setText("–")

    def set_battery_state(self, data):
        self.battery_info = data
        list_0_20 = list(range(0, 21))
        list_21_40 = list(range(21, 41))
        list_41_60 = list(range(41, 61))
        list_61_80 = list(range(61, 81))
        list_81_100 = list(range(81, 101))
        percentage = self.calculate_battery_percentage(data)
        # Wenn beide verschieden sind
        if not (self.previous_battery_percentage in list_0_20 and percentage in list_0_20 or self.previous_battery_percentage in list_21_40 and percentage in list_21_40 or self.previous_battery_percentage in list_41_60 and percentage in list_41_60 or self.previous_battery_percentage in list_61_80 and percentage in list_61_80 or self.previous_battery_percentage in list_81_100 and percentage in list_81_100):
            if percentage in list_0_20:
                self.ev3_battery_icon_label.setPixmap(QIcon(resource_path("ui/icons/battery-20.svg")).pixmap(QSize(14, 14)))
            elif percentage in list_21_40:
                self.ev3_battery_icon_label.setPixmap(QIcon(resource_path("ui/icons/battery-40.svg")).pixmap(QSize(14, 14)))
            elif percentage in list_41_60:
                self.ev3_battery_icon_label.setPixmap(QIcon(resource_path("ui/icons/battery-60.svg")).pixmap(QSize(14, 14)))
            elif percentage in list_61_80:
                self.ev3_battery_icon_label.setPixmap(QIcon(resource_path("ui/icons/battery-80.svg")).pixmap(QSize(14, 14)))
            elif percentage in list_81_100:
                self.ev3_battery_icon_label.setPixmap(QIcon(resource_path("ui/icons/battery-100.svg")).pixmap(QSize(14, 14)))
            self.previous_battery_percentage = percentage
        self.ev3_battery_label.setText(f"{percentage}%")
        self.battery_popup.set_battery_state(data)

    def calculate_battery_percentage(self, data):
        voltage_now = int(data["POWER_SUPPLY_VOLTAGE_NOW"]) / 1000000
        voltage_min = int(data["POWER_SUPPLY_VOLTAGE_MIN_DESIGN"]) / 10000000
        voltage_max = int(data["POWER_SUPPLY_VOLTAGE_MAX_DESIGN"]) / 10000000
        return round(max(0, min(100, (voltage_now - voltage_min) / (voltage_max - voltage_min) * 100)))

    def set_maximize_icon(self, icon_name):
        self.maximize_button.setIcon(QIcon(resource_path(f"ui/icons/{icon_name}.svg")))

    def on_frame_clicked(self):
        self.battery_popup.set_battery_state(self.battery_info)
        pos = self.ev3_frame.mapToGlobal(self.ev3_frame.rect().bottomLeft())
        pos.setY(pos.y() + 5)
        self.battery_popup.move(pos)
        self.battery_popup.show()

    def update_toolbar(self, tab):
        if tab is None:
            self.run_button.setEnabled(False)
            self.save_button.setEnabled(False)
            return
        self.save_button.setEnabled(tab.editable)
        is_python = tab.path.lower().endswith(".py")
        self.run_button.setEnabled(is_python or tab.executable)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.ev3_frame and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.on_frame_clicked()
                return True
        return super().eventFilter(watched, event)