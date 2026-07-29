from ev3_ide.core.resources import resource_path

class ThemeManager:
    def __init__(self, app):
        self.app = app
        self.current_theme = None

    def load_theme(self, theme_name):
        stylesheet_path = resource_path(f"ui/themes/{theme_name}.qss")

        with open(stylesheet_path, "r") as f:
            stylesheet = f.read()

        stylesheet = stylesheet.replace("{ICON_PATH}", resource_path("ui/icons"))

        self.app.setStyleSheet(stylesheet)
        self.current_theme = theme_name