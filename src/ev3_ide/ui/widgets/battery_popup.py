from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from ev3_ide.core.resources import resource_path


class BatteryPopup(QFrame):
    def __init__(self, ev3_frame, parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)

        self.ev3_frame = ev3_frame

        # self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFixedWidth(160)

        self.setObjectName("battery_popup")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(6)

        battery_layout = QHBoxLayout()
        battery_layout.setSpacing(2)
        battery_layout.setContentsMargins(0, 0, 5, 0)

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

        self.icon.setPixmap(QIcon(resource_path(f"ui/icons/{icon}")).pixmap(QSize(32, 32)))
        self.ev3_frame.update()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.ev3_frame.update()