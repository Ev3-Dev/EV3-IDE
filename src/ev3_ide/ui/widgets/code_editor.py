from PySide6.QtWidgets import QWidget, QPlainTextEdit, QTextEdit
from PySide6.QtGui import QFont, QFontDatabase, QPainter, QColor, QTextFormat
from PySide6.QtCore import Qt, QSize, QTimer

from ev3_ide.core.resources import resource_path


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.setObjectName("line_number_area")
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.paint_line_numbers(event)


class CodeEditor(QPlainTextEdit):
    _font_id = None
    _font_family = None

    def __init__(self, path, parent=None):
        super().__init__(parent)

        self.path = path

        self.setObjectName("code_editor")
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setFont(self.create_font_from_ttf(resource_path("ui/fonts/IdeMonoV3.ttf")))
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))

        self.line_number_padding_left = -16

        self.line_number_area = LineNumberArea(self)
        self.line_number_area.setObjectName("line_number_area")
        self.line_number_area.setFont(self.create_font_from_ttf(resource_path("ui/fonts/IdeMonoV3.ttf"), size=8))
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.line_number_area.update)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width()

        # Smoothes Scrollen
        self.friction = 0.80
        self.sensitivity = 0.01
        self.velocity = 0.0
        self.precise_value = float(self.verticalScrollBar().value())
        self.timer = QTimer(self)
        self.timer.setInterval(8)
        self.timer.timeout.connect(self.physics_tick)
        self.verticalScrollBar().valueChanged.connect(self.sync_on_manual_scroll)

    @classmethod
    def create_font_from_ttf(cls, ttf_path, size=10):
        if cls._font_family is None:
            cls._font_id = QFontDatabase.addApplicationFont(ttf_path)
            if cls._font_id == -1:
                return QFont()
            font_families = QFontDatabase.applicationFontFamilies(cls._font_id)
            if not font_families:
                return QFont()
            cls._font_family = font_families[0]
        return QFont(cls._font_family, size)

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        space = 15
        return space + self.fontMetrics().horizontalAdvance("9") * digits + space

    def update_line_number_area_width(self):
        self.setViewportMargins(self.line_number_area_width()-4, 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(cr.left(), cr.top(), self.line_number_area_width(), cr.height())

    def paint_line_numbers(self, event):
        painter = QPainter(self.line_number_area)
        background_color = self.line_number_area.palette().window().color()
        current_line_color = QColor("#26282e")
        painter.fillRect(event.rect(), background_color)
        current_block = self.textCursor().block()
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                if block == current_block:
                    painter.fillRect(0, int(top), self.line_number_area.width(), self.fontMetrics().height(), current_line_color)
                number = str(block_number + 1)
                painter.setPen(QColor("#888888"))
                painter.drawText(self.line_number_padding_left, int(top) + 2, self.line_number_area.width() - 8, int(self.fontMetrics().height()), Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
        painter.setPen(QColor("#313438"))
        painter.drawLine(self.line_number_area.width() - 1, event.rect().top(), self.line_number_area.width() - 1, event.rect().bottom())

    def highlight_current_line(self):
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor("#26282e"))
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

    # -------- Scrollen --------
    def sync_on_manual_scroll(self, value):
        if not self.timer.isActive():
            self.precise_value = float(value)
            self.velocity = 0.0

    def wheelEvent(self, event):
        steps = event.angleDelta().y()
        self.velocity += -(steps * self.sensitivity)
        if not self.timer.isActive():
            self.timer.start()
        event.accept()

    def physics_tick(self):
        scrollbar = self.verticalScrollBar()
        self.velocity *= self.friction
        if abs(self.velocity) < 0.1:
            self.velocity = 0.0
            self.timer.stop()
            return
        self.precise_value += self.velocity
        if self.precise_value < scrollbar.minimum():
            self.precise_value = float(scrollbar.minimum())
            self.velocity = 0.0
        elif self.precise_value > scrollbar.maximum():
            self.precise_value = float(scrollbar.maximum())
            self.velocity = 0.0
        scrollbar.setValue(int(round(self.precise_value)))