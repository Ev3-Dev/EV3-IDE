from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import QTimer, Signal, QPropertyAnimation, QEasingCurve, QPoint

from ev3_ide.core.resources import resource_path


class Notification(QFrame):
    closed = Signal()
    NOTIFICATION_ICONS = {"error": "ui/icons/notification_error.svg", "warning": "ui/icons/notification_warning.svg"}

    def __init__(self, title, message, notification_type="error", parent=None):
        super().__init__(parent)

        self.title = title
        self.message = message
        self.notification_type = notification_type

        self.setObjectName("notification")
        self.setFixedWidth(320)
        self.minimum_height = 72

        self.timer_duration = 6000

        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.out_animation = QPropertyAnimation(self, b"pos")
        self.out_animation.setDuration(300)
        self.out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.out_animation.finished.connect(self.closed.emit)

        self.go_up_animation = QPropertyAnimation(self, b"pos")
        self.go_up_animation.setDuration(300)
        self.go_up_animation.setEasingCurve(QEasingCurve.Type.OutBack)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(18, 18)
        icon_path = self.NOTIFICATION_ICONS.get(notification_type)
        if icon_path:
            self.icon_label.setPixmap(QIcon(resource_path(icon_path)).pixmap(18, 18))

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 11))
        self.title_label.setObjectName("notification_title")

        self.close_button = QPushButton()
        self.close_button.setFixedSize(20, 20)
        self.close_button.setIcon(QIcon(resource_path("ui/icons/close.svg")))
        self.close_button.setObjectName("notification_close_button")
        self.close_button.clicked.connect(self.close_notification)

        self.message_label = QLabel(message)
        self.message_label.setFont(QFont("Arial", 10))
        self.message_label.setObjectName("notification_message")
        self.message_label.setWordWrap(True)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        title_layout.addWidget(self.icon_label)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_button)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addSpacing(26)
        content_layout.addWidget(self.message_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 8, 9, 8)

        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addLayout(content_layout)
        layout.addStretch()

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close_notification)

    def stop_all_animations(self):
        self.animation.stop()
        self.out_animation.stop()
        self.go_up_animation.stop()

    def show_notification(self, target_pos, duration=6000):
        self.timer_duration = duration
        self.update_size()
        self.show()
        self.raise_()
        start_pos = QPoint(self.parentWidget().width() + 20, target_pos.y())
        self.stop_all_animations()
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(target_pos)
        self.animation.start()
        self.timer.start(self.timer_duration)

    def animate_to(self, target_pos):
        self.stop_all_animations()
        self.go_up_animation.setStartValue(self.pos())
        self.go_up_animation.setEndValue(target_pos)
        self.go_up_animation.start()

    def close_notification(self):
        self.timer.stop()
        self.stop_all_animations()
        end_pos = QPoint(self.parentWidget().width() + 20, self.y())
        self.out_animation.setStartValue(self.pos())
        self.out_animation.setEndValue(end_pos)
        self.out_animation.start()

    def update_size(self):
        width = self.width()
        contents_width = width - self.layout().contentsMargins().left() - self.layout().contentsMargins().right() - 26
        self.message_label.setFixedWidth(contents_width)
        message_height = self.message_label.heightForWidth(contents_width)
        height = self.layout().contentsMargins().top() + self.title_label.sizeHint().height() + self.layout().spacing() + message_height + self.layout().contentsMargins().bottom()
        self.setFixedHeight(max(self.minimum_height, height))

    def enterEvent(self, event):
        self.timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.timer.start(self.timer_duration)
        super().leaveEvent(event)


class NotificationManager:
    def __init__(self, parent):
        self.parent = parent
        self.timer_duration = 6000
        self.notifications = []

    def show(self, title, message, notification_type="error"):
        for n in self.notifications:
            if n.notification_type == notification_type and n.title == title and n.message == message:
                n.timer.stop()
                n.timer.start(self.timer_duration)
                self.reposition(False)
                return
        notification = Notification(title, message, notification_type, self.parent)
        notification.closed.connect(lambda: self.remove(notification))
        self.notifications.append(notification)
        self.reposition(True)

    def remove(self, notification):
        if notification not in self.notifications:
            return
        self.notifications.remove(notification)
        notification.deleteLater()
        self.reposition(True)

    def reposition(self, animation=False):
        margin = 15
        spacing = 10
        parent_rect = self.parent.rect()
        y = parent_rect.bottom() - margin
        for notification in reversed(self.notifications):
            notification.update_size()
            x = parent_rect.right() - notification.width() - margin
            y -= notification.height()
            target_pos = QPoint(x, y)
            if not notification.isVisible():
                notification.show_notification(target_pos, self.timer_duration)
            else:
                if animation:
                    notification.animate_to(target_pos)
                else:
                    notification.move(target_pos)
            y -= spacing