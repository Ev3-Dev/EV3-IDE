from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QMessageBox
from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QIcon, QShortcut, QKeySequence
from ev3_ide.ui.widgets.code_editor import CodeEditor
from ev3_ide.core.resources import resource_path


class EditorTab(QWidget):
    mark_unsaved = Signal()

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

        self.modified = False

        self.editor = CodeEditor(self.path)
        self.editor.setPlainText(self.content)
        self.editor.setReadOnly(not self.editable)
        self.editor.textChanged.connect(self.on_text_changed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.editor)

    def on_text_changed(self):
        if not self.modified:
            self.modified = True
            self.mark_unsaved.emit()


class EditorTabs(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("editor_tabs")
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setIconSize(QSize(18, 18))
        self.tabCloseRequested.connect(self.close_tab)
        # Shortcuts
        self.close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.close_tab_shortcut.activated.connect(self.close_current_tab)
        self.next_tab_shortcut = QShortcut(QKeySequence("Alt+Right"), self)
        self.next_tab_shortcut.activated.connect(self.next_tab)
        self.previous_tab_shortcut = QShortcut(QKeySequence("Alt+Left"), self)
        self.previous_tab_shortcut.activated.connect(self.previous_tab)

    def open_tab(self, data):
        # Datei bereits geöffnet?
        for index in range(self.count()):
            tab = self.widget(index)
            if isinstance(tab, EditorTab) and tab.path == data["path"]:
                self.setCurrentIndex(index)
                return
        tab = EditorTab(data)
        tab.mark_unsaved.connect(lambda: self.mark_tab_modified(tab))
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
            self.close_tab(index)

    def next_tab(self):
        if self.count() == 0:
            return
        index = self.currentIndex()
        next_index = (index + 1) % self.count()
        self.setCurrentIndex(next_index)

    def previous_tab(self):
        if self.count() == 0:
            return
        index = self.currentIndex()
        previous_index = (index - 1) % self.count()
        self.setCurrentIndex(previous_index)

    def mark_tab_modified(self, tab):
        if not tab.editable:
            return
        index = self.indexOf(tab)
        self.setTabText(index, f"{tab.name} *")

    def unmark_tab_modified(self, path):
        for index in range(self.count()):
            tab = self.widget(index)
            if isinstance(tab, EditorTab) and tab.path == path:
                tab.modified = False
                self.setTabText(index, tab.name)
                return

    def close_tab(self, index):
        tab = self.widget(index)
        if isinstance(tab, EditorTab) and tab.modified:
            result = QMessageBox.question(self, "Unsaved Changes", f"Die Datei „{tab.name}“ wurde geändert.\n" "Möchtest du die Änderungen speichern?", QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if result == QMessageBox.StandardButton.Cancel:
                return
            if result == QMessageBox.StandardButton.Save:
                # später: Speichern
                return
        self._close_tab(index)

    def _close_tab(self, index):
        self.removeTab(index)