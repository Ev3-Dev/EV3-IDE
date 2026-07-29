import paramiko
import subprocess
from ev3_ide.core.resources import resource_path

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ev3_username = "robot"
ev3_address = "ev3dev.local"
ev3_password = "maker"

remote_path_cpp = "/home/robot/main.cpp"
remote_path_bin = "/home/robot/main"

local_path_cpp = r"C:\Users\wanja\ev3_ide\src\ev3_ide\core\main.cpp"
local_path_bin = r"C:\Users\wanja\ev3_ide\src\ev3_ide\core\main"

print("Per SSH verbinden...")
ssh.connect(hostname=ev3_address, username=ev3_username, password=ev3_password, timeout=0.8, banner_timeout=0.8)

print("SFTP öffnen...")
sftp = ssh.open_sftp()
sftp.get(remote_path_cpp, local_path_cpp)

print("Kompilieren...")
try:
    result = subprocess.run([r"C:\Program Files (x86)\CodeSourcery\Sourcery G++ Lite\bin\arm-none-linux-gnueabi-g++.exe", "main.cpp", "-o", "main"], capture_output=True, text=True, check=True)
    print("Kompilierung erfolgreich!")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print("Fehler bei der Kompilierung:")
    print(e.stderr)

sftp.put(local_path_bin, remote_path_bin)
sftp.close()
ssh.close()