import time
import threading
import socket
import json
import struct
import paramiko
from PySide6.QtCore import QObject, Signal

from ev3_ide.core.resources import resource_path
from ev3_ide.core.ev3_dispatcher import EV3Dispatcher

class EV3Handler(QObject):
    ev3_connected = Signal()
    ev3_disconnected = Signal()
    message_received = Signal(dict)
    EV3_AGENT_PORT = 5000

    def __init__(self):
        super().__init__()

        self.dispatcher = EV3Dispatcher()
        self.message_received.connect(self.dispatcher.dispatch)

        self._ssh = None
        self._socket = None
        self._receive_thread = None
        self._stop_event = threading.Event()
        self.session_thread = None
        self.AGENT_SCRIPT_PATH = resource_path("core/agent.py")
        self.EV3_AGENT_PATH = "/home/robot/.ev3-ide/agent.py"
        self.EV3_IDE_DIR = "/home/robot/.ev3-ide/"

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


    def deploy_agent(self):
        if self._ssh is None:
            return False
        try:
            # Directory erstellen
            stdin, stdout, stderr = self._ssh.exec_command(f"mkdir -p '{self.EV3_IDE_DIR}'")
            exit_code = stdout.channel.recv_exit_status()
            if exit_code != 0:
                error = stderr.read().decode(errors="replace")
                raise RuntimeError(f"Verzeichnis konnte nicht erstellt werden: {error}")
            # Agent übertragen
            with self._ssh.open_sftp() as sftp:
                sftp.put(self.AGENT_SCRIPT_PATH, self.EV3_AGENT_PATH)
            # Ausführbar machen
            stdin, stdout, stderr = self._ssh.exec_command(f"chmod +x '{self.EV3_AGENT_PATH}'")
            exit_code = stdout.channel.recv_exit_status()
            if exit_code != 0:
                error = stderr.read().decode(errors="replace")
                raise RuntimeError(f"chmod fehlgeschlagen: {error}")
            print("Agent erfolgreich übertragen und ausführbar gemacht.")
            return True
        except Exception as e:
            print(f"Fehler: {e}")
            self.ev3_disconnected.emit()
            return False


    def start_agent(self):
        if self._ssh is None:
            return False
        try:
            self._ssh.exec_command(f"python3 '{self.EV3_AGENT_PATH}'")
            print("Agent-Startbefehl gesendet.")
            return True
        except Exception as e:
            print(f"Fehler beim Starten des Agents: {e}")
            self.ev3_disconnected.emit()
            return False


    def connect_to_agent(self):
        print("TCP-Verbindung zu:", self.ev3_address, self.EV3_AGENT_PORT)
        try:
            for attempt in range(30):
                try:
                    self._socket = socket.create_connection((self.ev3_address, self.EV3_AGENT_PORT), timeout=1.0)
                    break
                except (socket.timeout):
                    print("Erneut versuchen")
                    time.sleep(0.5)
            self._socket.settimeout(None)
            print("TCP-Verbindung zum Agent hergestellt.")
            self._receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._receive_thread.start()
            return True
        except Exception as e:
            print(f"TCP-Verbindung fehlgeschlagen: {e}")
            self.ev3_disconnected.emit()
            self._socket = None
            return False


    def send_message(self, message: dict):
        if self._socket is None:
            return
        data = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        header = struct.pack("!I", len(data))
        self._socket.sendall(header + data)


    def _receive_exactly(self, size: int) -> bytes:
        data = bytearray()
        while len(data) < size:
            chunk = self._socket.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Verbindung zum Agent wurde geschlossen.")
            data.extend(chunk)
        return bytes(data)


    def receive_message(self) -> dict:
        # Die Nachrichtenlänge herausfinden (die ersten 4 Bytes der Nachricht)
        header = self._receive_exactly(4)
        length = struct.unpack("!I", header)[0]
        data = self._receive_exactly(length)
        return json.loads(data.decode("utf-8"))


    def _receive_loop(self):
        while not self._stop_event.is_set():
            try:
                message = self.receive_message()
                print("EV3 → PC:", message)
                self.message_received.emit(message)
            except Exception as e:
                print(f"Verbindung zum Agent verloren: {e}")
                self.ev3_disconnected.emit()
                break


    def start_session(self):
        if self.session_thread and self.session_thread.is_alive():
            return
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
        if not self.deploy_agent():
            return
        if not self.start_agent():
            return
        if not self.connect_to_agent():
            return
        print("Agent gestartet")
        self.send_message({"type": "list_dir", "path": "/home/robot"})


    def stop(self):
        print("Stoppe EV3-Verbindung...")
        self._stop_event.set()
        self.ev3_disconnected.emit()
        if self._socket is not None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None