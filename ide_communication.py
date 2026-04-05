#!/usr/bin/env python3
import sys
import time
import threading
import struct
from ev3dev2.motor import list_motors
from ev3dev2.sensor import list_sensors
import json
import os
import subprocess
import shutil

WIDTH = 178
HEIGHT = 128
BPP = 4
FRAME_SIZE = WIDTH * HEIGHT * BPP

communication_types = {"screen": 1, "battery": 2, "motor": 3, "sensor": 4, "directory": 5, "file_content": 6, "stdin": 7, "stdout": 8, "stderr": 9, "program_finished": 0, "system_info": 11, "system_error": 12, "compilation_finished": 13, "install_uinput": 14, "install_ev3dev.h": 15, "install_ev3dev.cpp": 16, "install_libev3dev.a": 17}
running = True
compiling = False
executing = False
current_execute_process = None
current_compile_process = None
disable_screen_viewer = False
device = None
last_heartbeat = time.time()

write_lock = threading.Lock()

def send_message(msg_type: int, payload: bytes):
    try:
        with write_lock:
            sys.stdout.buffer.write(struct.pack("B", msg_type))
            sys.stdout.buffer.write(struct.pack("<I", len(payload)))
            sys.stdout.buffer.write(payload)
            sys.stdout.buffer.flush()
    except Exception:
        pass


dependencies_ready = {"ev3dev.h": True, "ev3dev.cpp": True, "libev3dev.a": True, "uinput": True}


if not os.path.isfile("/usr/local/include/ev3dev.h"):
    dependencies_ready["ev3dev.h"] = False
    send_message(communication_types["install_ev3dev.h"], "Install ev3dev.h".encode("utf-8"))
if not os.path.isfile("/usr/local/include/ev3dev.cpp"):
    dependencies_ready["ev3dev.cpp"] = False
    send_message(communication_types["install_ev3dev.cpp"], "Install ev3dev.cpp".encode("utf-8"))
if not os.path.isfile("/usr/local/lib/libev3dev.a"):
    dependencies_ready["libev3dev.a"] = False
    send_message(communication_types["install_libev3dev.a"], "Install libev3dev.a".encode("utf-8"))
missing_files = []
for file in ["ev3dev.h", "ev3dev.cpp", "libev3dev.a"]:
    if not dependencies_ready[file]:
        missing_files.append(file)
if missing_files:
    message = "'" + "', '".join(missing_files) + "' missing\nInstalling automatically..."
    send_message(communication_types["system_error"], message.encode("utf-8"))

site_packages = "/home/robot/.local/lib/python3.5/site-packages"
os.makedirs(site_packages, exist_ok=True)
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)
try:
    import uinput
except ImportError:
    dependencies_ready["uinput"] = False
    send_message(communication_types["system_error"], "module 'uinput' not installed\nInstalling automatically...".encode("utf-8"))
    send_message(communication_types["install_uinput"], "Install uinput".encode("utf-8"))


def display_thread():
    while running:
        if compiling or disable_screen_viewer:
            time.sleep(0.5)
            continue
        with open("/dev/fb0", "rb") as f:
            fb_data = f.read(FRAME_SIZE)
        send_message(communication_types["screen"], fb_data)
        time.sleep(0.1)

def battery_thread():
    while running:
        with open("/sys/class/power_supply/lego-ev3-battery/voltage_now") as f:
            voltage_now = int(f.read().strip())
        with open("/sys/class/power_supply/lego-ev3-battery/voltage_min_design") as f:
            voltage_min = int(f.read().strip())
        with open("/sys/class/power_supply/lego-ev3-battery/voltage_max_design") as f:
            voltage_max = int(f.read().strip())
        payload = struct.pack("<III", voltage_now, voltage_min, voltage_max)
        send_message(communication_types["battery"], payload)
        time.sleep(10)

def motor_thread():
    last_motor_dict = {}
    while running:
        if compiling:
            time.sleep(0.5)
            continue
        motor_dict = {}
        for m in list_motors():
            motor_dict[m.address] = m.driver_name
        if motor_dict == last_motor_dict:
            time.sleep(1)
            continue
        payload = json.dumps(motor_dict).encode("utf-8")
        send_message(communication_types["motor"], payload)
        last_motor_dict = motor_dict.copy()
        time.sleep(1)

def sensor_thread():
    last_sensor_dict = {}
    while running:
        if compiling:
            time.sleep(0.5)
            continue
        sensor_dict = {}
        for s in list_sensors():
            sensor_dict[s.address] = s.driver_name
        if sensor_dict == last_sensor_dict:
            time.sleep(1)
            continue
        payload = json.dumps(sensor_dict).encode("utf-8")
        send_message(communication_types["sensor"], payload)
        last_sensor_dict = sensor_dict.copy()
        time.sleep(1)

def send_directory_listing(path):
    try:
        entries = []
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            entries.append({"name": entry, "type": "dir" if os.path.isdir(full_path) else "file"})
        payload = json.dumps({"path": path, "entries": entries}).encode("utf-8")
        send_message(5, payload)
    except Exception as e:
        payload = json.dumps({"error": str(e)}).encode("utf-8")
        send_message(5, payload)

def read_stdout(process):
    for line in process.stdout:
        send_message(communication_types["stdout"], line.encode("utf-8"))

def read_stderr(process):
    for line in process.stderr:
        send_message(communication_types["stderr"], line.encode("utf-8"))

def command_thread():
    global running, last_heartbeat, compiling, executing, disable_screen_viewer, current_execute_process, current_compile_process, dependencies_ready, device
    if dependencies_ready["uinput"]:
        import uinput
        device = uinput.Device([uinput.KEY_ENTER, uinput.KEY_UP, uinput.KEY_DOWN, uinput.KEY_LEFT, uinput.KEY_RIGHT, uinput.KEY_BACKSPACE])
    while running:
        line = sys.stdin.buffer.readline()
        if not line:
            continue
        command = line.decode("utf-8").strip()
        # ------- Button-Presses --------
        if command.startswith("BUTTON"):
            if not dependencies_ready["uinput"]:
                send_message(communication_types["system_error"], "Screen Viewer not available\n'uinput' not installed".encode("utf-8"))
                continue
            button_to_press = command[7:].strip()
            if button_to_press == "enter":
                device.emit_click(uinput.KEY_ENTER)
            elif button_to_press == "up":
                device.emit_click(uinput.KEY_UP)
            elif button_to_press == "down":
                device.emit_click(uinput.KEY_DOWN)
            elif button_to_press == "right":
                device.emit_click(uinput.KEY_RIGHT)
            elif button_to_press == "left":
                device.emit_click(uinput.KEY_LEFT)
            elif button_to_press == "backspace":
                device.emit_click(uinput.KEY_BACKSPACE)
        # -------- Exit-Command --------
        elif command.startswith("EXIT"):
            running = False
        elif command.startswith("LIST_DIRECTORY"):
            path = command[15:].strip()
            send_directory_listing(path)
        elif command.startswith("OPEN"):
            if compiling:
                send_message(communication_types["system_error"], "Cannot open file while compiling".encode("utf-8"))
                continue
            if executing:
                send_message(communication_types["system_error"], "Cannot open file while executing".encode("utf-8"))
                continue
            path = command[5:].strip()
            if "." in path:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                    # Payload als JSON: Pfad + Inhalt
                    payload = json.dumps({"path": path, "content": file_content}).encode("utf-8")
                    send_message(communication_types["file_content"], payload)
                except Exception as e:
                    payload = json.dumps({"error": str(e), "path": path}).encode("utf-8")
                    send_message(communication_types["file_content"], payload)
        elif command.startswith("RUN_FILE"):
            if compiling:
                send_message(communication_types["system_error"], "Cannot run while compiling".encode("utf-8"))
                continue
            if executing:
                send_message(communication_types["system_error"], "Cannot run while executing".encode("utf-8"))
                continue
            path = command[9:].strip()
            current_execute_process = subprocess.Popen(["python3", "-u", path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
            executing = True
            threading.Thread(target=read_stdout, args=(current_execute_process,), daemon=True).start()
            threading.Thread(target=read_stderr, args=(current_execute_process,), daemon=True).start()
            def wait_for_finish(process):
                global executing
                process.wait()
                executing = False
                send_message(communication_types["program_finished"], "Exit code 0".encode("utf-8"))
            threading.Thread(target=wait_for_finish, args=(current_execute_process,), daemon=True).start()
        elif command.startswith("SAVE"):
            if compiling:
                send_message(communication_types["system_error"], "Cannot save while compiling".encode("utf-8"))
                continue
            if executing:
                send_message(communication_types["system_error"], "Cannot save while executing".encode("utf-8"))
                continue
            parts = command.split(" ", 2)
            if len(parts) != 3:
                send_message(communication_types["system_error"], "Error occurred while saving file: InvalidHeaderError".encode("utf-8"))
                continue
            _, path, length_str = parts
            try:
                length = int(length_str)
            except ValueError:
                send_message(communication_types["system_error"], "Error occurred while saving file: InvalidCommunicationLengthError".encode("utf-8"))
                continue
            code_bytes = sys.stdin.buffer.read(length)
            try:
                with open(path, "wb") as f:
                    f.write(code_bytes)
                send_message(communication_types["system_info"], "File saved successfully".encode("utf-8"))
            except Exception as e:
                error = "Error occurred while saving file: " + str(e)
                send_message(communication_types["system_error"], error.encode("utf-8"))
        elif command.startswith("RUN_TEMPORARY"):
            if compiling:
                send_message(communication_types["system_error"], "Cannot run while compiling".encode("utf-8"))
                continue
            if executing:
                send_message(communication_types["system_error"], "Cannot run while compiling".encode("utf-8"))
                continue
            parts = command.split(" ", 1)
            if len(parts) != 2:
                send_message(communication_types["system_error"],"Invalid RUN_TEMPORARY header".encode("utf-8"))
                continue
            try:
                length = int(parts[1])
            except ValueError:
                send_message(communication_types["system_error"],"Invalid RUN_TEMPORARY length".encode("utf-8"))
                continue
            code_bytes = sys.stdin.buffer.read(length)
            if len(code_bytes) != length:
                send_message(communication_types["system_error"],"Incomplete RUN_TEMPORARY data".encode("utf-8"))
                continue
            temp_path = "/home/robot/.EV3-IDE/_temporary_run.py"
            try:
                with open(temp_path, "wb") as f:
                    f.write(code_bytes)
                current_execute_process = subprocess.Popen(["python3", "-u", temp_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
                executing = True
                threading.Thread(target=read_stdout, args=(current_execute_process,), daemon=True).start()
                threading.Thread(target=read_stderr, args=(current_execute_process,), daemon=True).start()
                def wait_for_finish(process):
                    global executing
                    process.wait()
                    executing = False
                    send_message(communication_types["program_finished"],"Program finished".encode("utf-8"))
                threading.Thread(target=wait_for_finish, args=(current_execute_process,), daemon=True).start()
            except Exception as e:
                error = str(e)
                send_message(communication_types["stderr"], error.encode("utf-8"))
        elif command.startswith("INFO"):
            parts = command.split(" ", 1)
            if parts[1].strip() == "active":
                last_heartbeat = time.time()
        elif command.startswith("NEW_FILE"):
            if compiling:
                send_message(communication_types["system_error"], "Cannot create file while compiling".encode("utf-8"))
                continue
            if executing:
                send_message(communication_types["system_error"], "Cannot create file while executing".encode("utf-8"))
                continue
            parts = command.split(" ", 1)
            if len(parts) != 2:
                send_message(communication_types["system_error"],"Invalid NEW_FILE header".encode("utf-8"))
                continue
            file_path = parts[1].strip()
            try:
                if ".." in file_path:
                    raise ValueError("Invalid path")
                directory = os.path.dirname(file_path)
                if directory:
                    os.makedirs(directory, exist_ok=True)
                with open(file_path, "x"):
                    pass
                if file_path.lower().endswith(".py"):
                    os.chmod(file_path, 0o755)
                send_message(communication_types["system_info"], "File created successfully".encode("utf-8"))
                absolute_path = "/home/robot"
                send_directory_listing(absolute_path)
            except FileExistsError:
                send_message(communication_types["system_error"], "File already exists".encode("utf-8"))
            except Exception as e:
                send_message(communication_types["system_error"], str(e).encode("utf-8"))
        elif command.startswith("NEW_DIRECTORY"):
            if compiling:
                send_message(communication_types["system_error"], "Cannot create directory while compiling".encode("utf-8"))
                continue
            if executing:
                send_message(communication_types["system_error"], "Cannot create directory while executing".encode("utf-8"))
                continue
            parts = command.split(" ", 1)
            if len(parts) != 2:
                send_message(communication_types["system_error"], "Invalid NEW_DIRECTORY header".encode("utf-8"))
                continue
            directory_path = parts[1].strip()
            try:
                if ".." in directory_path:
                    raise ValueError("Invalid path")
                os.makedirs(directory_path, exist_ok=False)
                send_message(communication_types["system_info"], "Directory created successfully".encode("utf-8"))
                parent_dir = os.path.abspath(os.path.dirname(directory_path))
                send_directory_listing(parent_dir)
            except FileExistsError:
                send_message(communication_types["system_error"], "Directory already exists".encode("utf-8"))
            except Exception as e:
                send_message(communication_types["system_error"], str(e).encode("utf-8"))
        elif command.startswith("COMPILE"):
            if not dependencies_ready["ev3dev.h"] or not dependencies_ready["libev3dev.a"]:
                send_message(communication_types["system_error"], "C++ compilation not available\nMissing 'ev3dev.h' or 'libev3dev.a'".encode("utf-8"))
                send_message(communication_types["compilation_finished"], "Cannot compile".encode("utf-8"))
                continue
            parts = command.split(" ", 2)
            if len(parts) != 3:
                send_message(communication_types["system_error"], "Invalid COMPILE header".encode("utf-8"))
                continue
            input_file = parts[1].strip()
            output_file = parts[2].strip()
            def compile_thread():
                global compiling, current_compile_process
                msg = "Starting compilation...\nInput: " + input_file + "\nOutput: " + output_file
                send_message(communication_types["system_info"], msg.encode("utf-8"))
                compiling = True
                try:
                    current_compile_process = subprocess.Popen(["g++", input_file, "-o", output_file, "-lev3dev"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    current_compile_process.wait()
                    stderr = current_compile_process.stderr.read()
                    if current_compile_process.returncode == 0:
                        send_message(communication_types["system_info"], "Compilation successful".encode("utf-8"))
                    else:
                        send_message(communication_types["stderr"], stderr.encode("utf-8"))
                        if os.path.exists(output_file):
                            os.remove(output_file)
                    send_message(communication_types["compilation_finished"], "Compilation finished".encode("utf-8"))
                    send_directory_listing("/home/robot")
                except Exception as e:
                    send_message(communication_types["stderr"], str(e).encode("utf-8"))
                    send_message(communication_types["compilation_finished"], "Compilation finished".encode("utf-8"))
                    send_directory_listing("/home/robot")
                finally:
                    compiling = False
                    current_compile_process = None
            threading.Thread(target=compile_thread, daemon=True).start()
        elif command.startswith("DELETE"):
            if compiling:
                send_message(communication_types["system_error"], "Cannot delete while compiling".encode("utf-8"))
                continue
            if executing:
                send_message(communication_types["system_error"], "Cannot delete while executing".encode("utf-8"))
                continue
            parts = command.split(" ", 1)
            if len(parts) != 2:
                send_message(communication_types["system_error"], "Invalid DELETE header".encode("utf-8"))
                continue
            path = parts[1].strip()
            base_path = "/home/robot"
            if not path.startswith(base_path):
                send_message(communication_types["system_error"], "Invalid path".encode("utf-8"))
                continue
            if not os.path.exists(path):
                message = "Path does not exist: " + path
                send_message(communication_types["system_error"], message.encode("utf-8"))
                continue
            item_type = ""
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    item_type = "directory"
                else:
                    os.remove(path)
                    item_type = "file"
                message = "Successfully deleted " + item_type + "\nPath: " + path
                send_message(communication_types["system_info"], message.encode("utf-8"))
                send_directory_listing(base_path)
            except Exception as e:
                send_message(communication_types["system_error"], str(e).encode("utf-8"))
                continue
        elif command.startswith("EXECUTE"):
            if compiling:
                send_message(communication_types["system_error"], "Cannot execute while compiling".encode("utf-8"))
                continue
            if executing:
                send_message(communication_types["system_error"], "Cannot execute while executing".encode("utf-8"))
                continue
            parts = command.split(" ", 1)
            if len(parts) != 2:
                send_message(communication_types["system_error"], "Invalid EXECUTE header".encode("utf-8"))
                continue
            path = parts[1].strip()
            try:
                if not os.path.isfile(path):
                    msg = "Path is not a file or does not exist:\n" + path
                    send_message(communication_types["system_error"], msg.encode("utf-8"))
                    continue
                if not os.access(path, os.X_OK):
                    msg = "File is not executable:\n" + path
                    send_message(communication_types["system_error"], msg.encode("utf-8"))
                    continue
                msg = "Executing program...\nPath: " + path
                send_message(communication_types["system_info"], msg.encode("utf-8"))
                current_execute_process = subprocess.Popen([path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
                # Threads für Live-Output
                executing = True
                threading.Thread(target=read_stdout, args=(current_execute_process,), daemon=True).start()
                threading.Thread(target=read_stderr, args=(current_execute_process,), daemon=True).start()
                # Thread für Abschlussmeldung
                def wait_for_finish(proc):
                    global executing
                    proc.wait()
                    m = "Execution finished: " + path
                    executing = False
                    send_message(communication_types["program_finished"], m.encode("utf-8"))
                threading.Thread(target=wait_for_finish, args=(current_execute_process,), daemon=True).start()
            except Exception as e:
                send_message(communication_types["system_error"], str(e).encode("utf-8"))
        elif command.startswith("SCREEN_VIEWER"):
            if compiling:
                send_message(communication_types["system_error"], "Cannot toggle while compiling".encode("utf-8"))
                continue
            if executing:
                send_message(communication_types["system_error"], "Cannot toggle while executing".encode("utf-8"))
                continue
            parts = command.split(" ", 1)
            if len(parts) != 2:
                send_message(communication_types["system_error"], "Invalid TOGGLE header".encode("utf-8"))
                continue
            value = int(parts[1].strip())
            if value == 1:
                disable_screen_viewer = False
            elif value == 0:
                disable_screen_viewer = True
        elif command.startswith("RENAME"):
            if compiling:
                send_message(communication_types["system_error"], "Cannot rename while compiling".encode("utf-8"))
                continue
            if executing:
                send_message(communication_types["system_error"], "Cannot rename while executing".encode("utf-8"))
                continue
            parts = command.split(" ", 2)
            if len(parts) != 3:
                send_message(communication_types["system_error"], "Invalid RENAME header".encode("utf-8"))
                continue
            old_path = parts[1].strip()
            new_path = parts[2].strip()
            try:
                os.rename(old_path, new_path)
                send_message(communication_types["system_info"], "Rename successful".encode("utf-8"))
                base_path = "/home/robot"
                send_directory_listing(base_path)
            except Exception as e:
                send_message(communication_types["system_error"], str(e).encode("utf-8"))
        elif command.startswith("CANCEL_PROGRAM"):
            if current_execute_process:
                if current_execute_process.poll() is None:
                    current_execute_process.terminate()
                    send_message(communication_types["system_info"], "Execution cancelled".encode("utf-8"))
                    current_execute_process = None
                    executing = False
            else:
                send_message(communication_types["system_info"], "No process to cancel".encode("utf-8"))
        elif command.startswith("CANCEL_COMPILATION"):
            if not dependencies_ready["ev3dev.h"] or not dependencies_ready["libev3dev.a"]:
                send_message(communication_types["system_error"], "C++ compilation not available\nMissing 'ev3dev.h' or 'libev3dev.a'".encode("utf-8"))
                continue
            if current_compile_process:
                if current_compile_process.poll() is None:
                    current_compile_process.terminate()
                    compiling = False
                    current_compile_process = None
                    send_message(communication_types["system_info"], "Compilation cancelled".encode("utf-8"))
                    send_message(communication_types["compilation_finished"], "Compilation cancelled".encode("utf-8"))
                    send_directory_listing("/home/robot")
            else:
                send_message(communication_types["system_info"], "No process to cancel".encode("utf-8"))
        elif command.startswith("UINPUT_READY"):
            site_packages = "/home/robot/.local/lib/python3.5/site-packages"
            if site_packages not in sys.path:
                sys.path.insert(0, site_packages)
            try:
                import uinput
                device = uinput.Device([uinput.KEY_ENTER, uinput.KEY_UP, uinput.KEY_DOWN, uinput.KEY_LEFT, uinput.KEY_RIGHT, uinput.KEY_BACKSPACE])
                dependencies_ready["uinput"] = True
                send_message(communication_types["system_info"], "Module 'uinput' installed successfully".encode("utf-8"))
            except Exception as e:
                send_message(communication_types["system_error"], "Installation of module 'uinput' failed".encode("utf-8"))
                send_message(communication_types["stderr"], str(e).encode("utf-8"))
        elif command.startswith("EV3DEV_H_READY"):
            if os.path.isfile("/usr/local/include/ev3dev.h"):
                dependencies_ready["ev3dev.h"] = True
                send_message(communication_types["system_info"], "File 'ev3dev.h' installed successfully".encode("utf-8"))
            else:
                send_message(communication_types["system_error"], "Failed to install 'ev3dev.h'".encode("utf-8"))
        elif command.startswith("EV3DEV_CPP_READY"):
            if os.path.isfile("/usr/local/include/ev3dev.cpp"):
                dependencies_ready["ev3dev.cpp"] = True
                send_message(communication_types["system_info"], "File 'ev3dev.cpp' installed successfully".encode("utf-8"))
            else:
                send_message(communication_types["system_error"], "Failed to install 'ev3dev.cpp'".encode("utf-8"))
        elif command.startswith("LIBEV3DEV_A_READY"):
            if os.path.isfile("/usr/local/lib/libev3dev.a"):
                dependencies_ready["libev3dev.a"] = True
                send_message(communication_types["system_info"], "File 'libev3dev.a' installed successfully".encode("utf-8"))
            else:
                send_message(communication_types["system_error"], "Failed to install 'libev3dev.a'".encode("utf-8"))

def alive_check_thread():
    global running
    while running:
        now = time.time()
        if now - last_heartbeat > 10:
            send_message(communication_types["system_error"], "Communication to EV3 unreliable\nTry to restart this IDE and the EV3".encode("utf-8"))
            running = False
            break
        time.sleep(1)


threading.Thread(target=display_thread, daemon=True).start()
threading.Thread(target=battery_thread, daemon=True).start()
threading.Thread(target=command_thread, daemon=True).start()
threading.Thread(target=motor_thread, daemon=True).start()
threading.Thread(target=sensor_thread, daemon=True).start()
threading.Thread(target=alive_check_thread, daemon=True).start()

while running:
    time.sleep(1)
time.sleep(0.5)