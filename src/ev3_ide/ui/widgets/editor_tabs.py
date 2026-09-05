from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QIcon, QShortcut, QKeySequence
from ev3_ide.ui.widgets.code_editor import CodeEditor
from ev3_ide.core.resources import resource_path


class EditorTab(QWidget):
    def __init__(self, data):
        super().__init__()

        self.name = data["name"]
        self.path = data["path"]
        self.content = data["content"]
        self.size = data["size"]
        self.mode = data["mode"]
        self.last_time_modified = data["modified"]
        self.executable = data["executable"]
        self.editable = data["editable"]

        self.editor = CodeEditor(self.path)
        self.editor.setPlainText(self.content)
        print(f"Editable: {self.editable}")
        self.editor.setReadOnly(not self.editable)

        self.modified = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.editor)


class EditorTabs(QTabWidget):
    file_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setObjectName("editor_tabs")
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setIconSize(QSize(18, 18))
        self.tabCloseRequested.connect(self._close_tab)
        self.close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.close_tab_shortcut.activated.connect(self.close_current_tab)

    def open_tab(self, data):
        # Datei bereits geöffnet?
        for index in range(self.count()):
            tab = self.widget(index)
            if isinstance(tab, EditorTab) and tab.path == data["path"]:
                self.setCurrentIndex(index)
                return
        tab = EditorTab(data)
        tab.editor.textChanged.connect(lambda: self.file_changed.emit({"path": tab.path, "content": tab.editor.toPlainText()}))
        index = self.addTab(tab, tab.name)
        self.setTabToolTip(index, tab.path)
        if not tab.editable:
            self.setTabIcon(index, QIcon(resource_path("ui/icons/lock.svg")))
        self.setCurrentIndex(index)

    def handle_file_content(self, data):
        self.open_tab(data)

    def focus_tab(self, path):
        for index in range(self.count()):
            tab = self.widget(index)
            if isinstance(tab, EditorTab) and tab.path == path:
                self.setCurrentIndex(index)
                return

    def current_tab(self):
        tab = self.currentWidget()
        if isinstance(tab, EditorTab):
            return tab
        return None

    def current_content(self):
        tab = self.current_tab()
        if tab:
            return tab.editor.toPlainText()
        return None

    def current_path(self):
        tab = self.current_tab()
        if tab:
            return tab.path
        return None

    def get_opened_paths(self):
        paths = []
        for index in range(self.count()):
            tab = self.widget(index)
            if isinstance(tab, EditorTab):
                paths.append(tab.path)
        return paths

    def close_current_tab(self):
        index = self.currentIndex()
        if index >= 0:
            self._close_tab(index)

    def _close_tab(self, index):
        self.removeTab(index)