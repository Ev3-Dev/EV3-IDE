import threading

class EV3Sender:
    def __init__(self, ssh_container):
        self.ssh_container = ssh_container
        self.send_lock = threading.Lock()

    def send_message(self, message: str):
        ssh = self.ssh_container.ssh
        if not ssh:
            return
        try:
            with self.send_lock:
                ssh.stdin.write((message + "\n").encode("utf-8"))
                ssh.stdin.flush()
        except Exception:
            pass

    def send_bytes(self, data: bytes):
        ssh = self.ssh_container.ssh
        if not ssh:
            return
        try:
            with self.send_lock:
                ssh.stdin.write(data)
                ssh.stdin.flush()
        except Exception:
            pass