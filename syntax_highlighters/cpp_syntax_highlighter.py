import re

class CppSyntaxHighlighter:
    def __init__(self, editor):
        self.editor = editor
        self.CPP_KEYWORDS = ["int", "float", "double", "char", "bool", "void", "short", "long", "signed", "unsigned",
                            "if", "else", "switch", "case", "default", "for", "while", "do", "break", "continue", "return", "goto",
                            "class", "struct", "union", "enum", "public", "private", "protected", "friend", "namespace", "using",
                            "const", "constexpr", "volatile", "static", "inline", "virtual", "override", "final", "mutable",
                            "template", "typename", "new", "delete", "try", "catch", "throw", "auto", "decltype", "nullptr",
                            "true", "false", "alignas", "alignof", "char16_t", "char32_t", "noexcept", "static_assert",
                            "typeid", "sizeof", "dynamic_cast", "static_cast", "reinterpret_cast", "const_cast",
                            "export", "module", "import", "true", "false"]

    def highlight_syntax(self, code):
        # Strings checken, aber nicht highlighten
        def is_in_string(index, string_ranges):
            for start, end in string_ranges:
                if start <= index < end:
                    return True
            return False
        string_ranges = []
        for match in re.finditer(r"(\".*?\"|'.*?')", code):
            start = match.start()
            end = match.end()
            string_ranges.append((start, end))
            #self.editor.tag_add("string", f"1.0 + {start} chars", f"1.0 + {end} chars")
        # ---------------- Kommentare ----------------
        for match in re.finditer(r"//.*", code):
            if not is_in_string(match.start(), string_ranges):
                self.editor.tag_add("comment", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")
        for match in re.finditer(r"/\*.*?\*/", code, re.DOTALL):
            if not is_in_string(match.start(), string_ranges):
                self.editor.tag_add("comment", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")
        # ---------------- Strings ----------------
        for match in re.finditer(r"(\".*?\"|'.*?')", code):
            start = f"1.0 + {match.start()} chars"
            if "comment" not in self.editor.tag_names(start):
                self.editor.tag_add("string", start, f"1.0 + {match.end()} chars")
        # ---------------- Keywords ----------------
        pattern = r"\b(" + "|".join(self.CPP_KEYWORDS) + r")\b"
        for match in re.finditer(pattern, code):
            start = f"1.0 + {match.start()} chars"
            if not {"comment", "string"} & set(self.editor.tag_names(start)):
                self.editor.tag_add("keyword", start, f"1.0 + {match.end()} chars")
        # ---------------- Zahlen ----------------
        # Nur für normale Zahlen: r"\b\d+(\.\d+)?\b"
        for match in re.finditer(r"\b(0[xX][0-9a-fA-F]+|0[bB][01]+|0[0-7]+|\d+(\.\d+)?([eE][-+]?\d+)?)([uUlLfF]*)\b", code):
            start = f"1.0 + {match.start()} chars"
            if not {"comment", "string"} & set(self.editor.tag_names(start)):
                self.editor.tag_add("literal", start, f"1.0 + {match.end()} chars")
        # ---------------- Präprozessor ----------------
        for match in re.finditer(r"#\w+", code):
            start = f"1.0 + {match.start()} chars"
            if not {"comment", "string"} & set(self.editor.tag_names(start)):
                self.editor.tag_add("preprocessor", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")
        # ---------------- std ----------------
        for match in re.finditer(r"\bstd\b", code):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            if not {"comment", "string"} & set(self.editor.tag_names(start)):
                self.editor.tag_add("std", start, end)

    def handle_tab(self):
        cursor_index = self.editor.index("insert")
        # ---- C++-Snippets ----
        prev_2_index = f"{cursor_index} -2c"
        prev_4_index = f"{cursor_index} -4c"
        prev_5_index = f"{cursor_index} -5c"
        prev_6_index = f"{cursor_index} -6c"
        if self.editor.get(prev_5_index, cursor_index) == "!main":
            self.editor.delete(prev_5_index, cursor_index)
            self.editor.insert(cursor_index, "int main()\n{\n\t\n\treturn 0;\n}")
            cursor_line, cursor_col = cursor_index.split(".")
            self.editor.mark_set("insert", f"{int(cursor_line) + 2}.end")
            return "break"
        if self.editor.get(prev_4_index, cursor_index) == "!inc":
            self.editor.delete(prev_4_index, cursor_index)
            self.editor.insert(cursor_index, "#include <>")
            new_cursor_index = self.editor.index("insert")
            self.editor.mark_set("insert", f"{new_cursor_index} -1c")
            return "break"
        if self.editor.get(prev_5_index, cursor_index) == "!incs":
            self.editor.delete(prev_5_index, cursor_index)
            self.editor.insert(cursor_index, "#include <iostream>")
            return "break"
        if self.editor.get(prev_5_index, cursor_index) == "!cout":
            self.editor.delete(prev_5_index, cursor_index)
            self.editor.insert(cursor_index, 'cout << "\\n";')
            new_cursor_index = self.editor.index("insert")
            self.editor.mark_set("insert", f"{new_cursor_index} -4c")
            return "break"
        if self.editor.get(prev_6_index, cursor_index) == "!cout:":
            self.editor.delete(prev_6_index, cursor_index)
            self.editor.insert(cursor_index, 'std::cout << "\\n";')
            new_cursor_index = self.editor.index("insert")
            self.editor.mark_set("insert", f"{new_cursor_index} -4c")
            return "break"
        if self.editor.get(prev_4_index, cursor_index) == "!cin":
            self.editor.delete(prev_4_index, cursor_index)
            self.editor.insert(cursor_index, "cin >> ;")
            new_cursor_index = self.editor.index("insert")
            self.editor.mark_set("insert", f"{new_cursor_index} -1c")
            return "break"
        if self.editor.get(prev_5_index, cursor_index) == "!cin:":
            self.editor.delete(prev_5_index, cursor_index)
            self.editor.insert(cursor_index, "std::cin >> ;")
            new_cursor_index = self.editor.index("insert")
            self.editor.mark_set("insert", f"{new_cursor_index} -1c")
            return "break"
        if self.editor.get(prev_4_index, cursor_index) == "!cpp":
            self.editor.delete(prev_4_index, cursor_index)
            self.editor.insert(cursor_index, '#include <iostream>\n\nusing namespace std;\n\nint main()\n{\n\tcout << "\\n";\n\treturn 0;\n}')
            new_cursor_index = self.editor.index("insert")
            self.editor.mark_set("insert", f"{new_cursor_index} -2l + 9c")
            return "break"