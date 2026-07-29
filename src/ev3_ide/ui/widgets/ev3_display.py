from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from PIL import Image

EV3_W = 178
EV3_H = 128

class EV3Display(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 4)
        layout.setSpacing(4)

        title = QLabel("EV3-DISPLAY")
        title.setProperty("class", "sidebar-title")
        layout.addWidget(title)

        self.screen = QLabel()
        self.screen.setFixedSize(EV3_W * 2, EV3_H * 2)
        self.screen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screen.setStyleSheet("background: #1a2a1a; border-radius: 3px;")
        layout.addWidget(self.screen, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.show_blank()

    def show_blank(self):
        img = Image.new("RGB", (EV3_W, EV3_H), (20, 40, 20))
        self._set_image(img)

    def update_from_framebuffer(self, raw: bytes):
        import numpy as np
        arr  = np.frombuffer(raw, dtype=np.uint16).reshape(EV3_H, EV3_W)
        r    = ((arr >> 11) & 0x1F) << 3
        g    = ((arr >> 5)  & 0x3F) << 2
        b    = (arr & 0x1F) << 3
        img  = Image.fromarray(
            np.stack([r, g, b], axis=-1).astype("uint8")
        )
        self._set_image(img)

    def _set_image(self, img: Image.Image):
        img    = img.resize((EV3_W * 2, EV3_H * 2), Image.NEAREST)
        data   = img.tobytes("raw", "RGB")
        qimg   = QImage(data, EV3_W * 2, EV3_H * 2,
                        QImage.Format.Format_RGB888)
        self.screen.setPixmap(QPixmap.fromImage(qimg))