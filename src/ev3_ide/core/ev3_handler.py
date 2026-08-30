import threading
import paramiko
import stat
import posixpath
from PySide6.QtCore import QObject, Signal


class EV3Handler(QObject):
    ev3_connected = Signal()
    ev3_disconnected = Signal()
    error = Signal(str)

    directory_updated = Signal(list)
    file_read = Signal(str, str)
    file_written = Signal(str)

    output_received = Signal(str)
    process_finished = Signal(int)

    def __init__(self):
        super().__init__()

        self._ssh = None
        self._sftp = None
        self._shell = None
        self._stop_event = threading.Event()

        self.current_path = "/home/robot"

        self.ev3_username = "robot"
        self.ev3_address = "ev3dev.local"
        self.ev3_password = "maker"


    def check_available_and_connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=self.ev3_address, username=self.ev3_username, password=self.ev3_password, timeout=2.0, banner_timeout=5.0)
            return True, ssh
        except Exception:
            return False, None


    def start_session(self):
        self._stop_event.clear()
        self.session_thread = threading.Thread(target=self._start_session, daemon=True)
        self.session_thread.start()


    def _start_session(self):
        while True:
            if self._stop_event.wait(0.5):
                return
            result, ssh = self.check_available_and_connect()
            if result:
                self._ssh = ssh
                print("Connected")
                self.ev3_connected.emit()
                break
        self._sftp = self._ssh.open_sftp()
        self._shell = self._ssh.invoke_shell()
        self.list_dir("/home/robot")


    # -------- EV3-Funktionen --------
    def list_dir(self, path):
        threading.Thread(target=self._list_dir, args=(path,), daemon=True).start()

    def _list_dir(self, path):
        try:
            self.current_path = path
            entries = self._sftp.listdir_attr(path)
            result = []
            for entry in entries:
                entry_path = posixpath.join(path, entry.filename)
                result.append({
                    "name": entry.filename,
                    "path": entry_path,
                    "type": "directory" if stat.S_ISDIR(entry.st_mode) else "file",
                    "size": entry.st_size,
                    "mode": entry.st_mode,
                    "modified": entry.st_mtime,
                    "executable": bool(entry.st_mode & stat.S_IXUSR),
                })
            self.directory_updated.emit(result)
        except Exception as e:
            print(f"Fehler: {e}")

    def read_file(self, path):
        pass

    def write_file(self, path, content):
        pass

    def create_directory(self, path):
        pass

    def delete(self, path):
        pass

    def rename(self, old_path, new_path):
        pass

    def run_file(self, path):
        pass

    def go_back(self):
        self.list_dir(posixpath.dirname(self.current_path))



    def stop(self):
        self._stop_event.set()
        if self._shell is not None:
            self._shell.close()
            self._shell = None
        if self._sftp is not None:
            self._sftp.close()
            self._sftp = None
        if self._ssh is not None:
            self._ssh.close()
            self._ssh = None
        self.ev3_disconnected.emit()