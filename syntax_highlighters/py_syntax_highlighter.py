import re
import builtins
import keyword

class PySyntaxHighlighter:
    def __init__(self, editor):
        self.editor = editor
        self.STRING_REGEX = r'([furbFURB]?("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|".*?"|\'.*?\'))'

    def highlight_syntax(self, code):
        # Strings checken, aber nicht highlighten
        def is_in_string(index, string_ranges):
            for start, end in string_ranges:
                if start <= index < end:
                    return True
            return False
        string_ranges = []
        for match in re.finditer(self.STRING_REGEX, code):
            start = match.start()
            end = match.end()
            string_ranges.append((start, end))
            #self.editor.tag_add("string", f"1.0 + {start} chars", f"1.0 + {end} chars")
        # ---------------- Kommentare ----------------
        for match in re.finditer(r"#.*", code):
            start = match.start()
            if not is_in_string(start, string_ranges):
                self.editor.tag_add("comment", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")
        # ---------------- Strings ----------------
        # Nur normale Strings: r"(\".*?\"|'.*?')"
        for match in re.finditer(r'([furbFURB]?("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|".*?"|\'.*?\'))', code):
            start = f"1.0 + {match.start()} chars"
            if "comment" not in self.editor.tag_names(start):
                self.editor.tag_add("string", start, f"1.0 + {match.end()} chars")
        # ---------------- Keywords ----------------
        keywords = keyword.kwlist + ["True", "False", "None"]
        for match in re.finditer(r"\b(" + "|".join(keywords) + r")\b", code):
            start = f"1.0 + {match.start()} chars"
            if "comment" not in self.editor.tag_names(start):
                self.editor.tag_add("keyword", start, f"1.0 + {match.end()} chars")
        # ---------------- User-Funktionen sammeln ----------------
        user_funcs = set()
        for match in re.finditer(r"\bdef\s+([A-Za-z_][A-Za-z0-9_]*)", code):
            user_funcs.add(match.group(1))
            self.editor.tag_add("function", f"1.0 + {match.start(1)} chars", f"1.0 + {match.end(1)} chars")
        # ---------------- Funktionsaufrufe ----------------
        builtin_funcs = [x for x in dir(builtins) if x not in ("True", "False", "None")]
        all_funcs = set(builtin_funcs) | user_funcs
        func_call_pattern = r"\b(" + "|".join(map(re.escape, all_funcs)) + r")\s*\("
        for match in re.finditer(func_call_pattern, code):
            start = f"1.0 + {match.start(1)} chars"
            if not {"comment", "string"} & set(self.editor.tag_names(start)):
                self.editor.tag_add("function", start, f"1.0 + {match.end(1)} chars")
        # ---------------- Zahlen ----------------
        # Nur normale Zahlen: r"\b\d+(\.\d+)?([eE][-+]?\d+)?\b"
        # Nur normale und hexadezimale Zahlen: r"\b(0[xX][0-9a-fA-F]+|\d+(\.\d+)?([eE][-+]?\d+)?)\b"
        for match in re.finditer(r"\b(0[xX][0-9a-fA-F_]+|0[bB][01_]+|0[oO][0-7_]+|\d[\d_]*(\.\d[\d_]*)?([eE][-+]?\d[\d_]*)?)\b", code):
            start = f"1.0 + {match.start()} chars"
            if not {"comment", "string"} & set(self.editor.tag_names(start)):
                self.editor.tag_add("literal", start, f"1.0 + {match.end()} chars")
        # ---------------- Self ----------------
        for match in re.finditer(r"\bself\b", code):
            start = f"1.0 + {match.start()} chars"
            if not {"comment", "string"} & set(self.editor.tag_names(start)):
                self.editor.tag_add("self", start, f"1.0 + {match.end()} chars")

    def handle_tab(self):
        cursor_index = self.editor.index("insert")
        prev_2_index = f"{cursor_index} -2c"
        prev_4_index = f"{cursor_index} -4c"
        prev_5_index = f"{cursor_index} -5c"
        prev_6_index = f"{cursor_index} -6c"
        if self.editor.get(prev_6_index, cursor_index) == "!_main":
            self.editor.delete(prev_6_index, cursor_index)
            self.editor.insert(cursor_index, 'if __name__ == "__main__":\n\t')
            return "break"
        if self.editor.get(prev_5_index, cursor_index) == "!open":
            self.editor.delete(prev_5_index, cursor_index)
            self.editor.insert(cursor_index, 'with open("", "r") as f:\n\t')
            new_cursor_index = self.editor.index("insert")
            self.editor.mark_set("insert", f"{new_cursor_index} -1l +10c")
            return "break"
        if self.editor.get(prev_5_index, cursor_index) == "!init":
            self.editor.delete(prev_5_index, cursor_index)
            self.editor.insert(cursor_index, "def __init__(self, ):\n\t")
            new_cursor_index = self.editor.index("insert")
            self.editor.mark_set("insert", f"{new_cursor_index} -1l +18c")
            return "break"
        if self.editor.get(prev_6_index, cursor_index) == "!class":
            self.editor.delete(prev_6_index, cursor_index)
            self.editor.insert(cursor_index, "class :\n\tdef __init__(self):\n\t\tpass")
            new_cursor_index = self.editor.index("insert")
            self.editor.mark_set("insert", f"{new_cursor_index} linestart -2l +6c")
            return "break"
        if self.editor.get(prev_4_index, cursor_index) == "!try":
            self.editor.delete(prev_4_index, cursor_index)
            self.editor.insert(cursor_index, "try:\n\t\nexcept Exception:\n\tpass")
            new_cursor_index = self.editor.index("insert")
            self.editor.mark_set("insert", f"{new_cursor_index} linestart -2l +1c")
            return "break"
        if self.editor.get(prev_2_index, cursor_index) == "#!":
            self.editor.insert(cursor_index, "/usr/bin/env python3")
            return "break"