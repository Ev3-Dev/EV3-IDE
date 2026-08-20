from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy



class IDETitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        self.logo = QLabel("EV3")

        self.run_button = QPushButton("Run")

        # Windows-Buttons
        self.minimize_button = QPushButton("Minimize")

        self.maximize_button = QPushButton("Maximize")

        self.close_button = QPushButton("Close")

        layout.addWidget(self.logo)
        layout.addWidget(self.run_button)
        layout.addStretch()
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)


