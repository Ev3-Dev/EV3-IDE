import customtkinter as ctk
from ev3_sender import EV3Sender
import re
from syntax_highlighters.py_syntax_highlighter import PySyntaxHighlighter
from syntax_highlighters.cpp_syntax_highlighter import CppSyntaxHighlighter

class Editor:
    def __init__(self, root, ssh_container, register_layout_callback, console_height):
        # ------- Variablen --------
        self.root = root
        self.ssh_container = ssh_container
        self.ev3_sender = EV3Sender(ssh_container)
        self.KEYWORD_COLOR = "#FF6A50"
        self.FUNCTION_COLOR = "#5C8CD6"
        self.STRING_COLOR = "#4F8A2F"
        self.LITERAL_COLOR = "#BFCFF2"
        self.COMMENT_COLOR = "gray"
        self.PREPROCESSOR_COLOR = "#C586C0"
        self.SELF_COLOR = "#B8449C"
        self.STD_COLOR = "#B8449C"
        self.SPECIAL_CHARS = ["(", ")", "[", "]", "{", "}", '"', "'", ".", ",", ":", ";", "<", ">", "=", "?", "!", "+", "-", "*", "/", "#", "&", "|"]
        self.syntax_highlighting = ".py"
        self.is_file_saved = True
        self.syntax_highlighting_enabled = True
        self.CONSOLE_HEIGHT = console_height
        # -------- GUI-Elemente --------
        self.editor = ctk.CTkTextbox(self.root, height=self.root.winfo_height() - self.CONSOLE_HEIGHT - 85, width=self.root.winfo_width() - 587 - 15, font=("JetBrains Mono", 15), corner_radius=7, text_color="#D4D4D4", wrap="none", fg_color="#1C1A1A", undo=True, maxundo=100, spacing3=2)
        self.editor.configure(tabs=("1c",))
        self.editor.place(x=596, y=80)
        self.editor.tag_config("keyword", foreground=self.KEYWORD_COLOR)
        self.editor.tag_config("function", foreground=self.FUNCTION_COLOR)
        self.editor.tag_config("string", foreground=self.STRING_COLOR)
        self.editor.tag_config("literal", foreground=self.LITERAL_COLOR)
        self.editor.tag_config("comment", foreground=self.COMMENT_COLOR)
        self.editor.tag_config("preprocessor", foreground=self.PREPROCESSOR_COLOR)
        self.editor.tag_config("self", foreground=self.SELF_COLOR)
        self.editor.tag_config("std", foreground=self.STD_COLOR)
        self.ALL_TAGS = ["keyword", "function", "string", "literal", "comment", "preprocessor", "self", "std"]
        # -------- Syntax-Highlighter-Instanzen --------
        self.py_syntax_highlighter = PySyntaxHighlighter(self.editor)
        self.cpp_syntax_highlighter = CppSyntaxHighlighter(self.editor)
        # -------- Editor-Bindings --------
        # STRG+Backspace für Löschen ganzer Wörter
        self.editor.bind("<Control-BackSpace>", self.delete_prev_word)
        # Nach jedem Key: Syntax-Highlighting
        self.editor.bind("<KeyRelease>", self.highlight_syntax, add="+")
        # Nach jedem Key: Auto-Completion
        self.editor.bind("<KeyRelease>", self.auto_complete, add="+")
        # Nach Backspace: Löschen doppelter Special-Keys
        self.editor.bind("<BackSpace>", self.smart_backspace)
        # Nach Enter: neue Zeile und Einrückung einfügen
        self.editor.bind("<Return>", self.handle_return)
        # Nach Tab: Auf Shortcuts prüfen
        self.editor.bind("<Tab>", self.handle_tab)
        # Nach Shift+Tab: Einrückungen entfernen
        self.editor.bind("<Shift-Tab>", self.handle_shift_tab)
        # Nach STRG+linke Pfeiltaste: ein Wort zurückgehen
        self.editor.bind("<Control-Left>", self.jump_to_prev_word)
        # Nach STRG+rechte Pfeiltaste: ein Wort nach vorne gehen
        self.editor.bind("<Control-Right>", self.jump_to_next_word)
        # Callback hinzufügen
        register_layout_callback(self.update_layout)

    def update_layout(self, width, height, is_console_hidden, is_status_panel_hidden, event=None):
        if is_console_hidden:
            if is_status_panel_hidden:
                new_width = width - 10
                new_height = height - 85
                self.editor.configure(width=new_width, height=new_height)
            else:
                new_width = width - 587 - 15
                new_height = height - 85
                self.editor.configure(width=new_width, height=new_height)
        else:
            if is_status_panel_hidden:
                new_width = width - 10
                new_height = height - self.CONSOLE_HEIGHT - 90
                self.editor.configure(width=new_width, height=new_height)
            else:
                new_width = width - 587 - 15
                new_height = height - self.CONSOLE_HEIGHT - 90
                self.editor.configure(width=new_width, height=new_height)

    def delete_prev_word(self, event=None):
        if self.editor.tag_ranges("sel"):
            return None
        # Zuerst: smart_backspace prüfen
        result = self.smart_backspace(event)
        if result == "break":
            return "break"
        cursor_index = self.editor.index("insert")
        col = int(cursor_index.split(".")[1])
        cursor_line = int(cursor_index.split(".")[0])
        line_text = self.editor.get(f"{cursor_line}.0", f"{cursor_line}.end")
        if col == 0:
            self.editor.delete("insert -1c")
            return "break"
        i = col - 1
        # Am Anfang: Alle Leerzeichen löschen
        while i > 0 and line_text[i].isspace():
            i -= 1
        # Für normale Zeichen
        if line_text[i] not in self.SPECIAL_CHARS:
            while i > 0 and not line_text[i].isspace() and line_text[i] not in self.SPECIAL_CHARS:
                i -= 1
            # Da der Editor immer einen char zu viel löscht: Um einen verringern
            if i != 0 and col - i > 1:
                i += 1
            # Für Bug, wenn das erste Zeichen einer Zeile auch mit gelöscht wird, obwohl es ein special_char ist
            if i == 0 and line_text[0] in self.SPECIAL_CHARS:
                i += 1
            self.editor.delete(f"{cursor_line}.{i}", f"{cursor_line}.{col}")
        # Für Sonderzeichen: Alle gleichen aufeinanderfolgenden Sonderzeichen löschen
        else:
            char = line_text[i]
            while i > 0 and line_text[i] == char:
                i -= 1
            # Da der Editor immer einen char zu viel löscht: Um einen verringern
            if i != 0 and col - i > 1:
                i += 1
            # Für Bug, wenn das erste Zeichen einer Zeile auch mit gelöscht wird, obwohl es ein special_char ist
            if i == 0 and line_text[0] not in self.SPECIAL_CHARS and not line_text[0].isspace():
                i += 1
            self.editor.delete(f"{cursor_line}.{i}", f"{cursor_line}.{col}")
        return "break"

    def jump_to_prev_word(self, event=None):
        cursor_index = self.editor.index("insert")
        cursor_col = int(cursor_index.split(".")[1])
        cursor_line = int(cursor_index.split(".")[0])
        line_text = self.editor.get(f"{cursor_line}.0", f"{cursor_line}.end")
        if cursor_col == 0:
            self.editor.mark_set("insert", f"{cursor_index} -1c")
            return "break"
        i = cursor_col - 1
        while i > 0 and line_text[i].isspace():
            i -= 1
        if line_text[i] not in self.SPECIAL_CHARS:
            while i > 0 and not line_text[i].isspace() and line_text[i] not in self.SPECIAL_CHARS:
                i -= 1
            if i != 0 and cursor_col - i > 1:
                i += 1
            if i == 0 and line_text[0] in self.SPECIAL_CHARS:
                i += 1
            self.editor.mark_set("insert", f"{cursor_line}.{i}")
        else:
            char = line_text[i]
            while i > 0 and line_text[i] == char:
                i -= 1
            if i != 0 and cursor_col - i > 1:
                i += 1
            if i == 0 and line_text[0] not in self.SPECIAL_CHARS and not line_text[0].isspace():
                i += 1
            self.editor.mark_set("insert", f"{cursor_line}.{i}")
        return "break"

    def jump_to_next_word(self, event=None):
        cursor_index = self.editor.index("insert")
        cursor_col = int(cursor_index.split(".")[1])
        cursor_line = int(cursor_index.split(".")[0])
        line_text = self.editor.get(f"{cursor_line}.0", f"{cursor_line}.end")
        line_length = len(line_text)
        if cursor_col >= line_length:
            self.editor.mark_set("insert", f"{cursor_index} +1c")
            return "break"
        i = cursor_col
        while i < line_length and line_text[i].isspace():
            i += 1
        if i >= line_length:
            self.editor.mark_set("insert", f"{cursor_line}.{line_length}")
            return "break"
        if line_text[i] not in self.SPECIAL_CHARS:
            while i < line_length and not line_text[i].isspace() and line_text[i] not in self.SPECIAL_CHARS:
                i += 1
            self.editor.mark_set("insert", f"{cursor_line}.{i}")
        else:
            char = line_text[i]
            while i < line_length and line_text[i] == char:
                i += 1
            self.editor.mark_set("insert", f"{cursor_line}.{i}")
        return "break"

    def highlight_syntax(self, event=None):
        if self.syntax_highlighting_enabled:
            code = self.editor.get("1.0", "end-1c")
            # Tags aller Highlighter löschen
            for tag in self.ALL_TAGS:
                self.editor.tag_remove(tag, "1.0", "end")
            # Syntax-Highlighting-Aufruf
            if self.syntax_highlighting == ".py":
                self.py_syntax_highlighter.highlight_syntax(code)
            elif self.syntax_highlighting == ".cpp":
                self.cpp_syntax_highlighter.highlight_syntax(code)
        else:
            for tag in self.ALL_TAGS:
                self.editor.tag_remove(tag, "1.0", "end")

    def auto_complete(self, event=None):
        cursor_line, cursor_col = self.editor.index("insert").split(".")

        def reset_cursor():
            cursor_index = self.editor.index("insert")
            self.editor.mark_set("insert", f"{cursor_index} -1c")

        if event.char == "(" or event.keysym == "parenleft":
            self.editor.insert(f"{cursor_line}.{cursor_col}", ")")
            reset_cursor()
        elif (event.keysym == "8" and event.state & 0x8 and event.state & 0x4) or event.keysym == "bracketleft":
            self.editor.insert(f"{cursor_line}.{cursor_col}", "]")
            reset_cursor()
        elif (event.keysym == "7" and event.state & 0x8 and event.state & 0x4) or event.keysym == "braceleft":
            self.editor.insert(f"{cursor_line}.{cursor_col}", "}")
            reset_cursor()
        elif event.char == '"':
            self.editor.insert(f"{cursor_line}.{cursor_col}", '"')
            reset_cursor()
        elif event.char == "'":
            self.editor.insert(f"{cursor_line}.{cursor_col}", "'")
            reset_cursor()

        self.is_file_saved = False

    def handle_return(self, event=None):
        if self.editor.tag_ranges("sel"):
            return None
        cursor_line, cursor_col = self.editor.index("insert").split(".")
        current_line_text = self.editor.get(f"{cursor_line}.0", f"{cursor_line}.end")
        indentation = re.match(r"\s*", current_line_text).group(0)

        char_before = self.editor.get("insert -1c", "insert")
        char_after = self.editor.get("insert", "insert +1c")

        if char_before == ":":
            new_indent = indentation + "\t"
            self.editor.insert(f"{cursor_line}.{cursor_col}", f"\n{new_indent}")
            return "break"

        if char_before == "{" and char_after == "}":
            new_indent = indentation + "\t"
            # Nur EINEN Zeilenumbruch einfügen, Cursor an richtiger Stelle
            self.editor.insert(f"{cursor_line}.{cursor_col}", f"\n{new_indent}\n{indentation}")
            self.editor.mark_set("insert", f"{int(cursor_line) + 1}.{len(new_indent)}")
            return "break"
        else:
            # normales Verhalten: nur Einrücken übernehmen
            self.editor.insert(f"{cursor_line}.{cursor_col}", f"\n{indentation}")
            self.editor.mark_set("insert", f"{int(cursor_line) + 1}.{len(indentation)}")
            return "break"

    def smart_backspace(self, event=None):
        if self.editor.tag_ranges("sel"):
            return None
        cursor_index = self.editor.index("insert")
        prev_index = f"{cursor_index} -1c"
        try:
            prev_char = self.editor.get(prev_index)
            next_char = self.editor.get(cursor_index)
            prev_1_char = self.editor.get(f"{prev_index} -1c")
            prev_2_char = self.editor.get(f"{prev_index} -2c")
            prev_3_char = self.editor.get(f"{prev_index} -3c")
            next_2_char = self.editor.get(f"{cursor_index} +1c")
            next_3_char = self.editor.get(f"{cursor_index} +2c")
        except Exception:
            return "break"
        pairs = {'"': '"', "'": "'", "(": ")", "[": "]", "{": "}", "<": ">"}
        if prev_char in pairs and next_char == pairs[prev_char]:
            self.editor.delete(cursor_index)
            self.editor.delete(prev_index)
            return "break"
        if prev_char == "\t" and next_char == "\n" and prev_2_char == "{" and next_2_char == "}":
            self.editor.delete("insert -2c", "insert +1c")
            return "break"
        if prev_char == "\n" and next_char == "\n" and prev_1_char == "{" and next_3_char == "}":
            self.editor.delete("insert linestart -1c", "insert +1l lineend -1c")
            return "break"

    def handle_tab(self, event=None):
        if self.editor.tag_ranges("sel"):
            start_index = self.editor.index("sel.first")
            end_index = self.editor.index("sel.last")
            start_line = int(start_index.split(".")[0])
            end_line = int(end_index.split(".")[0])
            for line in range(start_line, end_line + 1):
                self.editor.insert(f"{line}.0", "\t")
            return "break"
        if self.syntax_highlighting == ".py":
            return self.py_syntax_highlighter.handle_tab()
        elif self.syntax_highlighting == ".cpp":
            return self.cpp_syntax_highlighter.handle_tab()

    def handle_shift_tab(self, event=None):
        if self.editor.tag_ranges("sel"):
            start_index = self.editor.index("sel.first")
            end_index = self.editor.index("sel.last")
            start_line = int(start_index.split(".")[0])
            end_line = int(end_index.split(".")[0])
            for line in range(start_line, end_line + 1):
                line_start = f"{line}.0"
                first_char = self.editor.get(line_start)
                if first_char == "\t":
                    self.editor.delete(line_start)
                elif self.editor.get(line_start, f"{line}.4") == "    ":
                    self.editor.delete(line_start, f"{line}.4")
            return "break"
        else:
            return None

    def configure_editor_height(self, new_height):
        self.editor.configure(height=new_height)

    def configure_editor_width(self, new_width):
        self.editor.configure(width=new_width)

    def get_content(self):
        return self.editor.get("1.0", "end-1c")

    def place_editor(self, x, y):
        self.editor.place(x=x, y=y)
