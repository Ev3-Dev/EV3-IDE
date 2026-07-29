import subprocess
import time
import threading
import struct
import json
import socket
import paramiko
from ev3_ide.core.resources import resource_path

class EV3Handler:
    def __init__(self):
        self._ssh = None
        self._shell = None
        self._response_buffer = None
        self.running = True
        self.session_thread = None
        self.AGENT_SCRIPT_PATH = resource_path("core/ev3_agent")
        self.EV3_AGENT_PATH = "/home/robot/.ev3-ide/agent"
        self.ev3_username = "robot"
        self.ev3_address = "ev3dev.local"
        self.ev3_password = "maker"

    def read_thread(self):
        pass

    def open_shell_and_start_agent(self) -> bool:
        if self._ssh is None:
            return False
        try:
            self._shell = self._ssh.invoke_shell()
            self._shell.settimeout(1.0)
            self._shell.send(f"{self.EV3_AGENT_PATH}\n")
            time.sleep(0.5)
            return True
        except Exception as e:
            return False

    def deploy_agent(self):
        if self._ssh is None:
            return False
        try:
            sftp = self._ssh.open_sftp()
            sftp.put(self.AGENT_SCRIPT_PATH, self.EV3_AGENT_PATH)
            sftp.close()
            return True
        except Exception as e:
            print(f"Fehler: {e}")
            return False

    def check_available_and_connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=self.ev3_address, username=self.ev3_username, password=self.ev3_password, timeout=0.8, banner_timeout=0.8)
            return True, ssh
        except Exception:
            return False, None

    #def terminate_threads(self):
    #    self.running = False
    #    current = threading.current_thread()
    #    if self.read_thread and self.read_thread.is_alive() and self.read_thread != current:
    #        self.read_thread.join(timeout=2)
    #    if self.session_thread and self.session_thread.is_alive() and self.session_thread != current:
    #        self.session_thread.join(timeout=2)
    #    if self.cleanup_thread and self.cleanup_thread.is_alive() and self.cleanup_thread != current:
    #        self.cleanup_thread.join(timeout=2)

    def start_session(self):
        if self.session_thread and self.session_thread.is_alive():
            return
        self.session_thread = threading.Thread(target=self._start_session, daemon=True)
        self.session_thread.start()

    def _start_session(self):
        while True:
            if not self.running:
                return
            result, ssh = self.check_available_and_connect()
            if result:
                self._ssh = ssh
                break
            time.sleep(0.1)
        self.deploy_agent()
        self.open_shell_and_start_agent()
        #self.kill_processes_before_start()
        #self.check_ev3_file()
        #self.ssh_container.ssh = subprocess.Popen(["ssh", f"robot@{self.ev3_name}.local", "python3", "/home/robot/.EV3-IDE/ide_communication.py"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, creationflags=self.CREATE_NO_WINDOW)
        #time.sleep(0.5)
        #self.ev3_sender.send_message("LIST_DIRECTORY /home/robot")
        #self.read_thread = threading.Thread(target=self.read_frames, daemon=True)
        #self.read_thread.start()

instance = EV3Handler()
instance.start_session()

while True:
    time.sleep(1)