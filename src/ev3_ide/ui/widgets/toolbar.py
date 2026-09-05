from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize, QEvent, QObject
from ev3_ide.core.resources import resource_path


class BatteryPopup(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)

        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFixedWidth(160)

        self.setObjectName("battery_popup")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        battery_layout = QHBoxLayout()
        battery_layout.setSpacing(2)

        self.icon = QLabel()

        self.percentage_label = QLabel("–")
        self.percentage_label.setObjectName("percentage_label")

        self.percent_sign_label = QLabel("%")
        self.percent_sign_label.setObjectName("percentage_sign_label")

        battery_layout.addStretch()
        battery_layout.addWidget(self.icon)
        battery_layout.addWidget(self.percentage_label)
        battery_layout.addWidget(self.percent_sign_label)
        battery_layout.addStretch()

        voltage_layout = QHBoxLayout()
        current_layout = QHBoxLayout()
        voltage_min_layout = QHBoxLayout()
        voltage_max_layout = QHBoxLayout()
        name_layout = QHBoxLayout()
        technology_layout = QHBoxLayout()

        self.voltage_label = QLabel("Voltage:")
        self.voltage_label.setObjectName("voltage_label")
        self.voltage_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.voltage_value_label = QLabel("–")
        self.voltage_value_label.setObjectName("voltage_value_label")
        self.voltage_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        voltage_layout.addWidget(self.voltage_label)
        voltage_layout.addStretch()
        voltage_layout.addWidget(self.voltage_value_label)

        self.current_label = QLabel("Current:")
        self.current_label.setObjectName("current_label")
        self.current_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.current_value_label = QLabel("–")
        self.current_value_label.setObjectName("current_value_label")
        self.current_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        current_layout.addWidget(self.current_label)
        current_layout.addStretch()
        current_layout.addWidget(self.current_value_label)

        self.voltage_min_label = QLabel("Voltage min:")
        self.voltage_min_label.setObjectName("voltage_min_label")
        self.voltage_min_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.voltage_min_value_label = QLabel("–")
        self.voltage_min_value_label.setObjectName("voltage_min_value_label")
        self.voltage_min_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        voltage_min_layout.addWidget(self.voltage_min_label)
        voltage_min_layout.addStretch()
        voltage_min_layout.addWidget(self.voltage_min_value_label)

        self.voltage_max_label = QLabel("Voltage max:")
        self.voltage_max_label.setObjectName("voltage_max_label")
        self.voltage_max_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.voltage_max_value_label = QLabel("–")
        self.voltage_max_value_label.setObjectName("voltage_max_value_label")
        self.voltage_max_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        voltage_max_layout.addWidget(self.voltage_max_label)
        voltage_max_layout.addStretch()
        voltage_max_layout.addWidget(self.voltage_max_value_label)

        self.name_label = QLabel("Name:")
        self.name_label.setObjectName("name_label")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.name_value_label = QLabel("–")
        self.name_value_label.setObjectName("name_value_label")
        self.name_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        name_layout.addWidget(self.name_label)
        name_layout.addStretch()
        name_layout.addWidget(self.name_value_label)

        self.technology_label = QLabel("Technology:")
        self.technology_label.setObjectName("technology_label")
        self.technology_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.technology_value_label = QLabel("–")
        self.technology_value_label.setObjectName("technology_value_label")
        self.technology_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        technology_layout.addWidget(self.technology_label)
        technology_layout.addStretch()
        technology_layout.addWidget(self.technology_value_label)

        layout.addLayout(battery_layout)
        layout.addLayout(voltage_layout)
        layout.addLayout(current_layout)
        layout.addLayout(voltage_min_layout)
        layout.addLayout(voltage_max_layout)
        layout.addLayout(name_layout)
        layout.addLayout(technology_layout)

    def calculate_battery_percentage(self, data):
        try:
            voltage_now = int(data.get("POWER_SUPPLY_VOLTAGE_NOW", "0")) / 1000000
            voltage_min = int(data.get("POWER_SUPPLY_VOLTAGE_MIN_DESIGN", "0")) / 10000000
            voltage_max = int(data.get("POWER_SUPPLY_VOLTAGE_MAX_DESIGN", "0")) / 10000000
            return round(max(0, min(100, (voltage_now - voltage_min) / (voltage_max - voltage_min) * 100)))
        except ZeroDivisionError:
            return 0

    def set_battery_state(self, data):
        # POWER_SUPPLY_NAME=lego-ev3-battery
        # POWER_SUPPLY_TECHNOLOGY=Li-ion
        # POWER_SUPPLY_VOLTAGE_NOW=7354000
        # POWER_SUPPLY_VOLTAGE_MAX_DESIGN=84000000
        # POWER_SUPPLY_VOLTAGE_MIN_DESIGN=60000000
        # POWER_SUPPLY_CURRENT_NOW=240000
        # POWER_SUPPLY_SCOPE=System

        percentage = self.calculate_battery_percentage(data)
        voltage = round(float(data.get("POWER_SUPPLY_VOLTAGE_NOW", "0")) / 1000000, 2)
        current = round(float(data.get("POWER_SUPPLY_CURRENT_NOW", "0")) / 1000000, 2)
        voltage_min = float(data.get("POWER_SUPPLY_VOLTAGE_MIN_DESIGN", "0")) / 10000000
        voltage_max = float(data.get("POWER_SUPPLY_VOLTAGE_MAX_DESIGN", "0")) / 10000000
        name = data.get("POWER_SUPPLY_NAME", "–")
        technology = data.get("POWER_SUPPLY_TECHNOLOGY", "–")

        self.percentage_label.setText(f"{percentage}")
        self.voltage_value_label.setText(f"{voltage} V")
        self.current_value_label.setText(f"{current} A")
        self.voltage_min_value_label.setText(f"{voltage_min} V")
        self.voltage_max_value_label.setText(f"{voltage_max} V")
        self.name_value_label.setText(f"{name}")
        self.technology_value_label.setText(f"{technology}")

        if percentage <= 20:
            icon = "battery-20.svg"
        elif percentage <= 40:
            icon = "battery-40.svg"
        elif percentage <= 60:
            icon = "battery-60.svg"
        elif percentage <= 80:
            icon = "battery-80.svg"
        else:
            icon = "battery-100.svg"

        self.icon.setPixmap(
            QIcon(resource_path(f"ui/icons/{icon}")).pixmap(QSize(32, 32))
        )


class IDETitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(40)

        self.ev3_state = "Disconnected"
        self.previous_battery_percentage = 0
        self.battery_info = {}

        self.battery_popup = BatteryPopup()

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 0, 0, 0)
        main_layout.setSpacing(5)

        self.ev3_frame = QFrame()
        self.ev3_frame.setObjectName("ev3_frame")
        self.ev3_frame.setFixedHeight(30)

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
        main_layout.addStretch(stretch=75)
        main_layout.addWidget(self.ev3_frame)
        main_layout.addWidget(self.ev3_help_button)
        main_layout.addStretch(stretch=1)
        main_layout.addLayout(windows_buttons_layout)

        self.ev3_frame.installEventFilter(self)

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

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.ev3_frame and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.on_frame_clicked()
                return True
        return super().eventFilter(watched, event)

    def on_frame_clicked(self):
        self.battery_popup.set_battery_state(self.battery_info)
        pos = self.ev3_frame.mapToGlobal(self.ev3_frame.rect().bottomLeft())
        self.battery_popup.move(pos)
        self.battery_popup.show()