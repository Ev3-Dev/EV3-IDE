from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

import keyword
import builtins
import inspect


class PythonHighlighter(QSyntaxHighlighter):

    NORMAL = 0
    TRIPLE_SINGLE = 1
    TRIPLE_DOUBLE = 2

    def __init__(self, document):
        super().__init__(document)

        # -----------------------------------------
        # Formate
        # -----------------------------------------
        self.formats = {"keyword": self.create_format("#cf8e6d"), "builtin_functions": self.create_format("#57aaf7"), "string": self.create_format("#6aab73"), "comment": self.create_format("#7a7e85"), "number": self.create_format("#2aacb8"), "operator": self.create_format("#d4d4d4"), "definition": self.create_format("#57aaf7")}


        # -----------------------------------------
        # Reguläre Ausdrücke
        # -----------------------------------------
        keywords = "|".join(QRegularExpression.escape(word) for word in keyword.kwlist)
        self.keyword_pattern = self.compile_pattern(rf"\b(?:{keywords})\b")

        builtin_functions = [name for name, obj in vars(builtins).items() if (inspect.isbuiltin(obj) or inspect.isfunction(obj) or isinstance(obj, type))]
        function_names = "|".join(QRegularExpression.escape(name) for name in builtin_functions)
        self.builtin_function_pattern = self.compile_pattern(rf"\b(?:{function_names})\b")

        self.number_pattern = self.compile_pattern(
            r"\b(?:"
            r"0[xX][0-9a-fA-F](?:_?[0-9a-fA-F])*|"
            r"0[bB][01](?:_?[01])*|"
            r"0[oO][0-7](?:_?[0-7])*|"
            r"(?:\d(?:_?\d)*(?:\.(?:\d(?:_?\d)*)?)?|\."
            r"\d(?:_?\d)*)"
            r"(?:[eE][+-]?\d(?:_?\d)*)?"
            r")\b"
        )

        self.operator_pattern = self.compile_pattern(
            r"\*\*=?|//=|>>=?|<<=?|"
            r"->|:=|"
            r"[+\-*/%@&|^~<>!=]=?|"
            r"//"
        )

        self.definition_pattern = self.compile_pattern(
            r"\bdef\s+([A-Za-z_]\w*)"
        )

        # -----------------------------------------
        # String-Präfixe und String-Erkennung
        # -----------------------------------------
        self.string_start_pattern = self.compile_pattern(
            r"(?i:[rubf]{1,2})?(?:'''|\"\"\"|'|\")"
        )

    # ---------------------------------------------
    # Hilfsfunktionen
    # ---------------------------------------------
    @staticmethod
    def create_format(color, bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        if bold:
            text_format.setFontWeight(QFont.Weight.Bold)
        return text_format

    @staticmethod
    def compile_pattern(pattern):
        expression = QRegularExpression(pattern)
        if not expression.isValid():
            raise ValueError(f"Ungültiger Regex: {expression.errorString()}")
        return expression

    @staticmethod
    def is_protected(position, protected_ranges):
        return any(start <= position < end for start, end in protected_ranges)

    # ---------------------------------------------
    # Strings und Kommentare
    # ---------------------------------------------
    def highlight_strings_and_comments(self, text):
        protected_ranges = []
        previous_state = self.previousBlockState()
        # Prüfen, ob der vorherige Block in einem
        # mehrzeiligen String geendet hat.
        if previous_state in (self.TRIPLE_SINGLE, self.TRIPLE_DOUBLE):
            delimiter = ("'''" if previous_state == self.TRIPLE_SINGLE else '"""')
            end = text.find(delimiter)
            if end == -1:
                self.setFormat(0, len(text), self.formats["string"])
                protected_ranges.append((0, len(text)))
                self.setCurrentBlockState(previous_state)
                return protected_ranges
            self.setFormat(0, end + 3, self.formats["string"])
            protected_ranges.append((0, end + 3))
            position = end + 3
        else:
            position = 0
        # Standardzustand für den aktuellen Block.
        self.setCurrentBlockState(self.NORMAL)

        # -----------------------------------------
        # Text von links nach rechts untersuchen
        # -----------------------------------------
        while position < len(text):
            # 1. Kommentare prüfen
            if text[position] == "#":
                self.setFormat(position, len(text) - position, self.formats["comment"])
                protected_ranges.append((position, len(text)))
                break
            # 2. NUR exakt an 'position' nach einem String-Start suchen!
            match = self.string_start_pattern.match(text, position, QRegularExpression.MatchType.NormalMatch, QRegularExpression.MatchOption.AnchorAtOffsetMatchOption,)
            if not match.hasMatch():
                position += 1
                continue
            start = match.capturedStart()
            delimiter_start = match.capturedEnd()
            prefix_and_delimiter = match.captured()
            # Bestimmen, ob es ein mehrzeiliger String ist.
            if prefix_and_delimiter.endswith("'''"):
                delimiter = "'''"
            elif prefix_and_delimiter.endswith('"""'):
                delimiter = '"""'
            else:
                delimiter = None

            # -------------------------------------
            # Mehrzeiliger String
            # -------------------------------------
            if delimiter is not None:
                end = text.find(delimiter, delimiter_start)
                if end == -1:
                    self.setFormat(start, len(text) - start, self.formats["string"])
                    protected_ranges.append((start, len(text)))
                    self.setCurrentBlockState(self.TRIPLE_SINGLE if delimiter == "'''" else self.TRIPLE_DOUBLE)
                    break
                end += 3

            # -------------------------------------
            # Einzeiliger String
            # -------------------------------------
            else:
                quote = text[delimiter_start - 1]
                end = delimiter_start
                while end < len(text):
                    if text[end] == "\\":
                        end += 2
                        continue
                    if text[end] == quote:
                        end += 1
                        break
                    end += 1
            # String formatieren
            self.setFormat(start, end - start, self.formats["string"])
            protected_ranges.append((start, end))
            position = end
        return protected_ranges

    # ---------------------------------------------
    # Andere Syntaxelemente
    # ---------------------------------------------
    def apply_pattern(self, text, pattern, text_format, protected_ranges, group=0):
        iterator = pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            start = match.capturedStart(group)
            length = match.capturedLength(group)
            if start < 0 or length <= 0:
                continue
            end = start + length
            if self.is_protected(start, protected_ranges):
                continue
            if any(start < protected_end and end > protected_start for protected_start, protected_end in protected_ranges):
                continue
            self.setFormat(start, length, text_format)

    # ---------------------------------------------
    # Syntax Highlighting
    # ---------------------------------------------
    def highlightBlock(self, text):
        # 1. Strings und Kommentare erkennen
        protected_ranges = (self.highlight_strings_and_comments(text))
        # 2. Keywords
        self.apply_pattern(text, self.keyword_pattern, self.formats["keyword"], protected_ranges)
        # 3. Builtin-Funktionen
        self.apply_pattern(text, self.builtin_function_pattern, self.formats["builtin_functions"], protected_ranges)
        # 4. Zahlen
        self.apply_pattern(text, self.number_pattern, self.formats["number"], protected_ranges)
        # 5. Operatoren
        self.apply_pattern(text, self.operator_pattern, self.formats["operator"], protected_ranges)
        # 6. Funktionsdefinitionen
        self.apply_pattern(text, self.definition_pattern, self.formats["definition"], protected_ranges, group=1)