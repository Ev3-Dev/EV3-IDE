from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
import keyword
import re


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.rules = []

        # Schlüsselwörter
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#c586c0"))
        self.keyword_format.setFontWeight(QFont.Weight.Bold)

        for word in keyword.kwlist:
            pattern = rf"\b{re.escape(word)}\b"
            self.rules.append((re.compile(pattern), self.keyword_format))

        # Zeichenketten: einfache und doppelte Anführungszeichen
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#ce9178"))

        self.rules.append((re.compile(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\""), self.string_format))

        # Zahlen
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#b5cea8"))

        self.rules.append((re.compile(r"\b(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\b"), self.number_format))

        # Kommentare
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6a9955"))

        self.rules.append((re.compile(r"#.*"), self.comment_format))

        # Operatoren
        self.operator_format = QTextCharFormat()
        self.operator_format.setForeground(QColor("#d4d4d4"))

        self.rules.append((re.compile(r"[+\-*/%=<>!&|^~]+"), self.operator_format))

        # Funktions- und Klassendefinitionen
        self.definition_format = QTextCharFormat()
        self.definition_format.setForeground(QColor("#dcdcaa"))

        self.rules.append((re.compile(r"\b(?:def|class)\s+([A-Za-z_]\w*)"), self.definition_format))

    def highlightBlock(self, text):
        for pattern, text_format in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), text_format)