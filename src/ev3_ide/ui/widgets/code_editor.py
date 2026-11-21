from PySide6.QtWidgets import QWidget, QPlainTextEdit, QTextEdit
from PySide6.QtGui import QFont, QFontDatabase, QPainter, QColor, QTextFormat, QTextCursor, QTextCharFormat
from PySide6.QtCore import Qt, QSize, QTimer
from pathlib import Path

from ev3_ide.core.resources import resource_path
from ev3_ide.ui.widgets.syntax_highlighters.python_highlighter import PythonHighlighter


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.setObjectName("line_number_area")
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.paint_line_numbers(event)

    def wheelEvent(self, event):
        self.code_editor.wheelEvent(event)


class CodeEditor(QPlainTextEdit):
    _font_id = None
    _font_family = None

    PAIRS = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}

    def __init__(self, path, parent=None):
        super().__init__(parent)

        self.path = path

        self.highlighter = None
        self.set_highlighter()

        self.bracket_format = QTextCharFormat()
        self.bracket_format.setBackground(QColor("#454545"))
        self.bracket_format.setForeground(QColor("#ffffff"))

        self.current_line_format = QTextCharFormat()
        self.current_line_format.setBackground(QColor("#26282e"))
        self.current_line_format.setProperty(QTextFormat.Property.FullWidthSelection, True)

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
        self.cursorPositionChanged.connect(self.update_extra_selections)
        self.update_extra_selections()
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

    def set_path(self, new_path):
        self.path = new_path
        self.set_highlighter()

    def set_highlighter(self):
        suffix = Path(self.path).suffix.lower()
        if self.highlighter is not None:
            self.highlighter.setDocument(None)
            self.highlighter.deleteLater()
            self.highlighter = None
        if suffix == ".py":
            self.highlighter = PythonHighlighter(self.document())

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
        # self.line_number_area.update()

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

    def update_extra_selections(self):
        selections = []
        selections.extend(self.get_current_line_selection())
        selections.extend(self.get_bracket_selections())
        self.setExtraSelections(selections)

    def get_current_line_selection(self):
        selection = QTextEdit.ExtraSelection()
        selection.format = self.current_line_format
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        return [selection]

    def get_bracket_selections(self):
        doc = self.document()
        pos = self.textCursor().position()
        doc_len = doc.characterCount()
        brackets = {"(": ")", "[": "]", "{": "}"}
        reverse_brackets = {")": "(", "]": "[", "}": "{"}
        target_pos = -1
        for candidate in (pos - 1, pos):
            if 0 <= candidate < doc_len:
                ch = doc.characterAt(candidate)
                if ch in brackets or ch in reverse_brackets:
                    target_pos = candidate
                    break
        if target_pos == -1:
            return []
        char = doc.characterAt(target_pos)
        if char in brackets:
            opening, closing, step = char, brackets[char], 1
            limit = min(doc_len, target_pos + 5000)
        else:
            opening, closing, step = reverse_brackets[char], char, -1
            limit = max(-1, target_pos - 5000)
        depth = 0
        match_position = -1
        for i in range(target_pos, limit, step):
            c = doc.characterAt(i)
            if c == opening:
                depth += step
            elif c == closing:
                depth -= step
            if depth == 0:
                match_position = i
                break
        selections = []
        if match_position != -1:
            for bracket_pos in (target_pos, match_position):
                selection = QTextEdit.ExtraSelection()
                selection.format = self.bracket_format
                selection.cursor = QTextCursor(doc)
                selection.cursor.setPosition(bracket_pos)
                selection.cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor,)
                selections.append(selection)
        return selections

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

    def keyPressEvent(self, event):
        if self.isReadOnly():
            super().keyPressEvent(event)
            return

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.insertPlainText("\n")
            return

        cursor = self.textCursor()

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Aktuelle Zeile ermitteln
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            line = cursor.block().text()
            # Einrückung der aktuellen Zeile übernehmen
            indentation = ""
            for char in line:
                if char in (" ", "\t"):
                    indentation += char
                else:
                    break
            # Text vor und nach dem Cursor
            current_cursor = self.textCursor()
            position = current_cursor.positionInBlock()
            text_before = line[:position]
            text_after = line[position:]
            # Prüfen, ob der Cursor zwischen { und } steht
            if text_before.rstrip().endswith("{") and text_after.lstrip().startswith("}"):
                cursor = self.textCursor()
                cursor.insertText("\n" + indentation + "    " + "\n" + indentation)
                # Cursor in die eingerückte Zeile setzen
                cursor.movePosition(QTextCursor.MoveOperation.Up)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                self.setTextCursor(cursor)
                return
            # Normale Einrückung übernehmen
            self.textCursor().insertText("\n" + indentation)
            return

        if event.key() == Qt.Key.Key_Backspace and not cursor.hasSelection():
            position = cursor.position()
            text = self.toPlainText()
            if 0 < position < len(text):
                char_before = text[position - 1]
                char_after = text[position]
                if self.PAIRS.get(char_before) == char_after:
                    cursor.movePosition(QTextCursor.MoveOperation.Left)
                    cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 2)
                    cursor.removeSelectedText()
                    return

        char = event.text()
        if char in self.PAIRS:
            closing = self.PAIRS[char]
            # Falls Text markiert ist, diesen einklammern
            if cursor.hasSelection():
                selected_text = cursor.selectedText()
                cursor.insertText(char + selected_text + closing)
                return
            # Öffnendes und schließendes Zeichen einfügen
            cursor.insertText(char + closing)
            # Cursor zwischen die beiden Zeichen setzen
            cursor.movePosition(QTextCursor.MoveOperation.Left)
            self.setTextCursor(cursor)
            return

        super().keyPressEvent(event)