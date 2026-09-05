import threading
import paramiko
import stat
import posixpath
import queue
import time
from PySide6.QtCore import QObject, Signal


class SFTPWorker(QObject):
    directory_updated = Signal(list)
    file_loaded = Signal(dict)
    file_written = Signal(str)
    battery_updated = Signal(dict)

    output_received = Signal(str)
    process_finished = Signal(int)
    error = Signal(dict)

    def __init__(self, sftp):
        super().__init__()
        self.sftp = sftp
        self.queue = queue.Queue()
        self.stop_event = threading.Event()
        self.current_path = "/home/robot"

    def enqueue(self, function, *args):
        self.queue.put((function, args))

    def is_connected(self):
        return self.sftp is not None

    def run(self):
        self.get_battery()
        last_battery_check = time.monotonic()
        while not self.stop_event.is_set():
            now = time.monotonic()
            if now - last_battery_check >= 10:
                self.get_battery()
                last_battery_check = now
            try:
                function, args = self.queue.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                function(*args)
            except Exception as e:
                self.error.emit({"message": str(e), "type": "error"})
            finally:
                self.queue.task_done()

    def stop(self):
        self.stop_event.set()
        if self.sftp is not None:
            self.sftp.close()
            self.sftp = None

    # -------- SFTP-Aktionen --------

    def list_dir(self, path):
        if not self.is_connected():
            return
        try:
            self.current_path = path
            entries = self.sftp.listdir_attr(path)
            result = []
            protected_paths = ["/sys", "/proc", "/dev"]
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
                    "editable": bool(entry.st_mode & stat.S_IWUSR) and not any(entry_path.startswith(path) for path in protected_paths),
                })
            self.directory_updated.emit(result)
        except Exception as e:
            self.error.emit({"message": str(e), "type": "error"})

    def get_file(self, data):
        path = data["path"]
        if not self.is_connected():
            return
        try:
            with self.sftp.open(path, "rb") as file:
                header = file.read(4096)
                if header.startswith(b"\x1f\x8b"):
                    self.error.emit({"path": path, "message": "GZIP-Dateien können nicht als Text geöffnet werden."})
                    return
                if b"\x00" in header:
                    self.error.emit({"path": path, "message": "Die Datei scheint eine Binärdatei zu sein."})
                    return
                data_read = header + file.read()
            content = data_read.decode("utf-8")
            self.file_loaded.emit({**data, "content": content})
        except UnicodeDecodeError:
            self.error.emit({"path": path, "message": "Die Datei ist keine UTF-8-Textdatei."})
        except Exception as e:
            self.error.emit({"path": path, "message": str(e)})

    def go_back(self):
        self.list_dir(posixpath.dirname(self.current_path))

    def go_home(self):
        self.list_dir("/home/robot")

    def refresh(self):
        self.list_dir(self.current_path)

    def get_battery(self):
        if not self.is_connected():
            return
        try:
            with self.sftp.open("/sys/class/power_supply/lego-ev3-battery/uevent", "rb") as file:
                data = file.read().decode("utf-8")
                values = {}
                for line in data.splitlines():
                    if "=" in line:
                        key, value = line.split("=", 1)
                        values[key] = value
                self.battery_updated.emit(values)
        except Exception as e:
            self.error.emit({"message": str(e), "type": "battery"})


class EV3Handler(QObject):
    ev3_connected = Signal()
    ev3_disconnected = Signal()

    directory_updated = Signal(list)
    file_loaded = Signal(dict)
    file_written = Signal(str)
    battery_updated = Signal(dict)

    output_received = Signal(str)
    process_finished = Signal(int)
    error = Signal(dict)

    def __init__(self):
        super().__init__()

        self._ssh = None
        self._sftp = None
        self._shell = None
        self.session_thread = None
        self._worker = None
        self._worker_thread = None
        self._stop_event = threading.Event()

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
                # print("Connected")
                self.ev3_connected.emit()
                break
        self._sftp = self._ssh.open_sftp()
        self._shell = self._ssh.invoke_shell()

        self._worker = SFTPWorker(self._sftp)
        self._worker.directory_updated.connect(self.directory_updated)
        self._worker.file_loaded.connect(self.file_loaded)
        self._worker.file_written.connect(self.file_written)
        self._worker.battery_updated.connect(self.battery_updated)
        self._worker.output_received.connect(self.output_received)
        self._worker.process_finished.connect(self.process_finished)
        self._worker.error.connect(self.error)

        self._worker_thread = threading.Thread(target=self._worker.run, daemon=True)

        self._worker_thread.start()

        self.list_dir("/home/robot")


    # -------- Öffentliche API --------
    def list_dir(self, data):
        if self._worker is None:
            return
        self._worker.enqueue(self._worker.list_dir, data)

    def get_file(self, path):
        if self._worker is None:
            return
        self._worker.enqueue(self._worker.get_file, path)

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
        if self._worker is None:
            return
        self._worker.enqueue(self._worker.go_back)

    def go_home(self):
        if self._worker is None:
            return
        self._worker.enqueue(self._worker.go_home)

    def refresh(self):
        if self._worker is None:
            return
        self._worker.enqueue(self._worker.refresh)

    def stop(self):
        if self._worker is not None:
            self._worker.stop()
        if self._ssh is not None:
            self._ssh.close()
            self._ssh = None