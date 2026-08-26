from PySide6.QtCore import QObject, Signal

class EV3Dispatcher(QObject):
    dir_listing_received = Signal(dict)

    def __init__(self):
        super().__init__()

    def dispatch(self, message):
        message_type = message.get("type")
        if message_type == "dir_listing":
            self.dir_listing_received.emit(message)
        else:
            print("Unbekannter Nachrichtentyp:", message_type)