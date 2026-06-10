import subprocess
import time
import threading
import struct
import json
from ev3_sender import EV3Sender

class EV3Handler:
        def __init__(self, gui, root, ssh_container, notification_manager):
            self.gui = gui
            self.root = root
            self.ssh_container = ssh_container
            self.notification_manager = notification_manager
            self.session_thread = None
            self.read_thread = None
            self.cleanup_thread = None
            self.running = True
            self.ev3_name = "ev3dev"
            self.communication_types = {"screen": 1, "battery": 2, "motor": 3, "sensor": 4, "directory": 5, "file_content": 6, "stdin": 7, "stdout": 8, "stderr": 9, "program_finished": 0, "system_info": 11, "system_error": 12, "compilation_finished": 13, "install_uinput": 14, "install_ev3dev.h": 15, "install_ev3dev.cpp": 16, "install_libev3dev.a": 17}
            self.root.protocol("WM_DELETE_WINDOW", self.delete_window)
            self.CREATE_NO_WINDOW = 0x08000000

        def check_reachable(self, call_gui=False):
            try:
                subprocess.run(["ssh", "-o", "BatchMode=yes", "robot@ev3dev.local", "echo", "ok"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=self.CREATE_NO_WINDOW)
            except subprocess.CalledProcessError:
                if call_gui:
                    self.root.after(0, lambda: self.gui.device_disconnected(show_notification=False))
                return False
            if call_gui:
                self.root.after(0, self.gui.device_connected, self.ev3_name)
            return True

        def kill_processes_before_start(self):
            try:
                subprocess.run(["ssh", "robot@ev3dev.local", "pkill -f python3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=self.CREATE_NO_WINDOW)
                time.sleep(0.1)
            except Exception:
                pass

        def soft_kill_after_start(self):
            try:
                self.ev3_sender.send_message("EXIT")
            except Exception:
                pass

        def check_ev3_file(self):
            remote_dir = "/home/robot/.EV3-IDE"
            local_file = "ide_communication.py"
            remote_file = f"{remote_dir}/ide_communication.py"
            try:
                # Ordner erstellen, falls er fehlt
                subprocess.run(["ssh", "robot@ev3dev.local", f"mkdir -p {remote_dir}"], check=True, creationflags=self.CREATE_NO_WINDOW)
                # Datei überschreiben
                subprocess.run(["scp", local_file, f"robot@ev3dev.local:{remote_file}"], check=True, creationflags=self.CREATE_NO_WINDOW)
            except subprocess.CalledProcessError as e:
                self.notification_manager.show_message(self.root, "Error", "Unable to update system files on EV3")

        def copy_uinput_to_ev3(self):
            def copy_thread():
                local_dir = "ev3_dependencies/python_uinput"
                remote_dir = "/home/robot/.local/lib/python3.5/site-packages"
                try:
                    subprocess.run(["ssh", "robot@ev3dev.local", "mkdir", "-p", "/home/robot/.local/lib/python3.5/site-packages"], check=True, creationflags=self.CREATE_NO_WINDOW)
                    subprocess.run(["scp", "-r", f"{local_dir}/*", f"robot@ev3dev.local:{remote_dir}/"], check=True, creationflags=self.CREATE_NO_WINDOW)
                    time.sleep(0.5)
                    self.ev3_sender.send_message("UINPUT_READY")
                except Exception as e:
                    self.notification_manager.show_message(self.root, "Error", "Installation of module 'uinput' failed\nTry commands in README.md")
            threading.Thread(target=copy_thread, daemon=True).start()

        def copy_ev3dev_h_to_ev3(self):
            def copy_thread():
                local_file = "ev3_dependencies/ev3dev.h"
                safe_path = "/home/robot/.EV3-IDE"
                remote_path = "/usr/local/include/ev3dev.h"
                try:
                    subprocess.run(["scp", f"{local_file}", f"robot@ev3dev.local:{safe_path}/"], check=True, creationflags=self.CREATE_NO_WINDOW)
                    subprocess.run(["ssh", "robot@ev3dev.local", "sudo", "mv", f"{safe_path}/ev3dev.h", f"{remote_path}"], check=True, creationflags=self.CREATE_NO_WINDOW)
                    time.sleep(0.5)
                    self.ev3_sender.send_message("EV3DEV_H_READY")
                except Exception:
                    self.notification_manager.show_message(self.root, "Error", "Installation of 'ev3dev.h' failed\nTry commands in README.md")
            threading.Thread(target=copy_thread, daemon=True).start()

        def copy_ev3dev_cpp_to_ev3(self):
            def copy_thread():
                local_file = "ev3_dependencies/ev3dev.cpp"
                safe_path = "/home/robot/.EV3-IDE"
                remote_path = "/usr/local/include/ev3dev.cpp"
                try:
                    subprocess.run(["scp", f"{local_file}", f"robot@ev3dev.local:{safe_path}/"], check=True, creationflags=self.CREATE_NO_WINDOW)
                    subprocess.run(["ssh", "robot@ev3dev.local", "sudo", "mv", f"{safe_path}/ev3dev.cpp", f"{remote_path}"], check=True, creationflags=self.CREATE_NO_WINDOW)
                    time.sleep(0.5)
                    self.ev3_sender.send_message("EV3DEV_CPP_READY")
                except Exception:
                    self.notification_manager.show_message(self.root, "Error", "Installation of 'ev3dev.cpp' failed\nTry commands in README.md")
            threading.Thread(target=copy_thread, daemon=True).start()

        def copy_libev3dev_a_to_ev3(self):
            def copy_thread():
                local_file = "ev3_dependencies/libev3dev.a"
                safe_path = "/home/robot/.EV3-IDE"
                remote_path = "/usr/local/lib/libev3dev.a"
                try:
                    subprocess.run(["scp", f"{local_file}", f"robot@ev3dev.local:{safe_path}/"], check=True, creationflags=self.CREATE_NO_WINDOW)
                    subprocess.run(["ssh", "robot@ev3dev.local", "sudo", "mv", f"{safe_path}/libev3dev.a", f"{remote_path}"], check=True, creationflags=self.CREATE_NO_WINDOW)
                    time.sleep(0.5)
                    self.ev3_sender.send_message("LIBEV3DEV_A_READY")
                except Exception:
                    self.notification_manager.show_message(self.root, "Error", "Installation of 'libev3dev.a' failed\nTry commands in README.md")
            threading.Thread(target=copy_thread, daemon=True).start()

        def read_exact(self, n):
            data = b""
            while len(data) < n:
                chunk = self.ssh_container.ssh.stdout.read(n - len(data))
                if not chunk:
                    self.gui.device_disconnected()
                    raise EOFError
                data += chunk
            return data

        def read_message(self):
            msg_type = struct.unpack("B", self.read_exact(1))[0]
            length = struct.unpack("<I", self.read_exact(4))[0]
            payload = self.read_exact(length)
            return msg_type, payload

        def read_frames(self):
            while self.running:
                try:
                    msg_type, payload = self.read_message()
                    if msg_type == self.communication_types["screen"]:
                        self.root.after(0, self.gui.update_screen, payload)
                    elif msg_type == self.communication_types["battery"]:
                        v_now, v_min, v_max = struct.unpack("<III", payload)
                        self.root.after(0, self.gui.update_battery, v_now, v_min, v_max)
                    elif msg_type == self.communication_types["motor"]:
                        motor_dict = json.loads(payload.decode("utf-8"))
                        self.root.after(0, self.gui.update_motors, motor_dict)
                    elif msg_type == self.communication_types["sensor"]:
                        sensor_dict = json.loads(payload.decode("utf-8"))
                        self.root.after(0, self.gui.update_sensors, sensor_dict)
                    elif msg_type == self.communication_types["directory"]:
                        directory_data = json.loads(payload.decode("utf-8"))
                        self.root.after(0, self.gui.update_directory, directory_data)
                    elif msg_type == self.communication_types["file_content"]:
                        file_content = json.loads(payload.decode("utf-8"))
                        self.root.after(0, self.gui.open_file, file_content)
                    elif msg_type == self.communication_types["stdout"] or msg_type == self.communication_types["stderr"]:
                        content = payload.decode("utf-8")
                        self.gui.update_console_std("stdout" if msg_type == self.communication_types["stdout"] else "stderr", content)
                    elif msg_type == self.communication_types["program_finished"]:
                        self.gui.ev3_program_finished()
                    elif msg_type == self.communication_types["system_info"]:
                        self.notification_manager.show_message(self.root, "Info", payload.decode("utf-8"))
                    elif msg_type == self.communication_types["system_error"]:
                        self.notification_manager.show_message(self.root, "Error", payload.decode("utf-8"), duration=5000)
                    elif msg_type == self.communication_types["compilation_finished"]:
                        self.gui.compilation_finished()
                    elif msg_type == self.communication_types["install_uinput"]:
                        self.copy_uinput_to_ev3()
                    elif msg_type == self.communication_types["install_ev3dev.h"]:
                        self.copy_ev3dev_h_to_ev3()
                    elif msg_type == self.communication_types["install_ev3dev.cpp"]:
                        self.copy_ev3dev_cpp_to_ev3()
                    elif msg_type == self.communication_types["install_libev3dev.a"]:
                        self.copy_libev3dev_a_to_ev3()
                except EOFError:
                    self.running = False
                    self.gui.device_disconnected()
                    return

        def delete_window(self):
            if not self.gui.editor.is_file_saved:
                self.gui.directory_updater.save_file()
            self.root.destroy()
            def cleanup_ev3():
                if hasattr(self, "ev3_sender"):
                    try:
                        self.ev3_sender.send_message("EXIT")
                    except Exception:
                        self.kill_processes_before_start()
                time.sleep(0.5)
                self.running = False
                if self.ssh_container.ssh:
                    self.ssh_container.ssh.terminate()
            self.cleanup_thread = threading.Thread(target=cleanup_ev3, daemon=True)
            self.cleanup_thread.start()

        def reconnect(self):
            self.running = False
            # Editor und Konsole leeren
            self.gui.editor.editor.delete("1.0", "end")
            self.gui.console.delete_all()
            self.gui.update_console("Select a file")
            # Kurzzeitig auf False setzen
            self.stop_session()
            self.root.after(1000, self._restart_session)

        def _restart_session(self):
            self.running = True
            self.start_session()

        def stop_session(self):
            if hasattr(self, "ev3_sender"):
                try:
                    self.ev3_sender.send_message("EXIT")
                except Exception:
                    pass
            if self.ssh_container.ssh:
                try:
                    self.ssh_container.ssh.terminate()
                    self.ssh_container.ssh.wait(timeout=2)
                    if self.ssh_container.ssh.stdout:
                        self.ssh_container.ssh.stdout.close()
                    if self.ssh_container.ssh.stdin:
                        self.ssh_container.ssh.stdin.close()
                except Exception:
                    pass
                self.ssh_container.ssh = None
            self.terminate_threads()

        def terminate_threads(self):
            self.running = False
            current = threading.current_thread()
            if self.read_thread and self.read_thread.is_alive() and self.read_thread != current:
                self.read_thread.join(timeout=2)
            if self.session_thread and self.session_thread.is_alive() and self.session_thread != current:
                self.session_thread.join(timeout=2)
            if self.cleanup_thread and self.cleanup_thread.is_alive() and self.cleanup_thread != current:
                self.cleanup_thread.join(timeout=2)

        def start_session(self):
            if self.session_thread and self.session_thread.is_alive():
                return
            self.session_thread = threading.Thread(target=self._start_session, daemon=True)
            self.session_thread.start()

        def _start_session(self):
            while self.running and not self.check_reachable(call_gui=True):
                time.sleep(0.5)
            if not self.running:
                return
            self.kill_processes_before_start()
            self.check_ev3_file()
            self.ssh_container.ssh = subprocess.Popen(["ssh", f"robot@{self.ev3_name}.local", "python3", "/home/robot/.EV3-IDE/ide_communication.py"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, creationflags=self.CREATE_NO_WINDOW)
            self.ev3_sender = EV3Sender(self.ssh_container)
            time.sleep(0.5)
            self.ev3_sender.send_message("LIST_DIRECTORY /home/robot")
            self.read_thread = threading.Thread(target=self.read_frames, daemon=True)
            self.read_thread.start()