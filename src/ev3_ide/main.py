from PySide6.QtWidgets import QApplication
from ev3_ide.ui.main_window import MainWindow
from ev3_ide.core.theme_manager import ThemeManager

def main():
    app = QApplication([])

    theme_manager = ThemeManager(app)
    theme_manager.load_theme("dark")

    window = MainWindow(app, theme_manager)
    window.show()

    app.exec()

if __name__ == "__main__":
    main()