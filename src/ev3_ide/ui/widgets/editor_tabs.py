from PySide6.QtWidgets import QTabWidget
from PySide6.QtCore import Signal
from ev3_ide.ui.widgets.code_editor import CodeEditor

class EditorTabs(QTabWidget):
    file_changed = Signal(str, str)  # Pfad, Inhalt

    def __init__(self):
        super().__init__()
        self.setObjectName("editor_tabs")
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self._close_tab)
        self._paths: dict[int, str] = {}  # Tab-Index → Remote-Pfad

    def open_file(self, data):
        # Schon offen? Dann nur fokussieren
        for i, p in self._paths.items():
            if p == data["path"]:
                self.setCurrentIndex(i)
                return

        content = ""

        editor = CodeEditor()
        if content:
            editor.setPlainText(content)
        else:
            editor.setPlainText("")
        editor.textChanged.connect(lambda: self.file_changed.emit(data["path"], editor.toPlainText()))

        name  = data["name"]
        index = self.addTab(editor, name)
        self._paths[index] = data["path"]
        self.setCurrentIndex(index)

    def current_content(self) -> str | None:
        w = self.currentWidget()
        return w.toPlainText() if w else None

    def current_path(self) -> str | None:
        return self._paths.get(self.currentIndex())

    def mark_unsaved(self, index: int):
        name = self.tabText(index)
        if not name.startswith("● "):
            self.setTabText(index, f"● {name}")

    def mark_saved(self, index: int):
        name = self.tabText(index).removeprefix("● ")
        self.setTabText(index, name)

    def _close_tab(self, index: int):
        self.removeTab(index)
        self._paths.pop(index, None)
        # Indizes neu aufbauen
        self._paths = {i: p for i, (_, p) in enumerate(sorted(self._paths.items()))}