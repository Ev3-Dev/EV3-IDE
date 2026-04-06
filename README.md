# EV3-IDE

**EV3-IDE** is a lightweight development environment for the LEGO Mindstorms EV3.  
It supports C++ and Python development and automatically installs required libraries on the EV3.

---

## Requirements

* Windows 10 or Windows 11 (64-bit)
* EV3 running ev3dev2

Linux and macOS support may be added in future versions.

* EV3 host name must be 'ev3dev' (the default one).

> **Note:** This program is designed around `ev3dev2`. It only works if your EV3 is running this specific OS. Get it at [https://www.ev3dev.org/downloads/](https://www.ev3dev.org/downloads/).

---

## Features

* **Real-time Status Updater:** View the EV3 screen and device status live.
* **Directory Viewer:** Browse, add, rename, or delete EV3 files from within the IDE (by right-clicking on a file or directory to access the context menu).
* **Code Editor:** Full-featured editor with syntax highlighting for Python and C++.
* **Integrated Console:** Run programs directly on the EV3 and see output and errors in real-time.  
* **Automatic EV3 File Management:** Installs required system files (`ev3dev.h`, `ev3dev.cpp`, `libev3dev.a`).  
* **Python Module Support:** Automatically installs Python modules like `python-uinput`.

---
  
## EV3 Prerequisites

To allow the IDE to automatically copy files into system folders, the user must perform the following setup **once**:

### 1. Passwordless SSH Access

To let the IDE transfer files via `scp` directly to the EV3:

**1.1** Connect the EV3 via a USB cable to your computer.

**1.2** Open a PowerShell terminal on your PC (Windows start menu → search for `powershell`).

**1.3** Generate an SSH key if you don’t already have one:

```powershell
ssh-keygen
```
* If you are asked whether to overwrite an existing key, type `n` and press Enter.
* If you are asked for a file location, use the default one by pressing the Enter key.
* If you are asked for a passphrase, simply press Enter. Do it twice if you have to repeat the passphrase.

**1.4** Copy the public key to the EV3:

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh robot@ev3dev.local "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

* If you are asked whether you want to allow a connection and have the options '(yes, no, [fingerprint])', type `yes`.
* If you are asked for a password for 'robot', enter your password for the EV3 (the default one is `maker`; if you haven't changed it, this will be it).

**1.5**  After this, the IDE can connect to the EV3 without asking for a password. Try to connect manually:

```powershell
ssh robot@ev3dev.local
```
When connecting to your EV3 now, there should be no password request.

### 2. `sudo` Without Password for File Operations

To allow the IDE to copy system files such as `/usr/local/include/ev3dev.h`:

**2.1** Log in to the EV3 as `robot`:

```powershell
ssh robot@ev3dev.local
```

**2.2** Run `sudo visudo`:

```powershell
sudo visudo
```

**2.3** Add the following line at the end of the file and save the change afterwards (via `Ctrl+x`, then type `y` and press Enter):

```powershell
robot ALL=(ALL) NOPASSWD:ALL
```

This lets the IDE move required system files without prompting for a password.

---

## Installation

### Download

1. Go to the Releases page: [https://github.com/Ev3-Dev/EV3-IDE/releases](https://github.com/Ev3-Dev/EV3-IDE/releases)

2. Download the latest version

3. Extract the ZIP file

4. Run `EV3-IDE.exe`

5. Connect the EV3 via USB.

6. The IDE will automatically check if the ev3dev files are present.

7. (optional) Add a desktop shortcut to be able to start it more easily.

### Build from Source (optional)

Requirements:
* Python 3.13
* PyInstaller

Open PowerShell (or CMD) and navigate to the project folder: `cd C:\path\to\EV3-IDE`

Run the following command to build the IDE:

```bash
pyinstaller --noconsole --onedir --clean --add-data "images;images" --add-data "ide_communication.py;." --add-data "ev3_dependencies;ev3_dependencies" --add-data "fonts;fonts" --icon=images/ev3.ico --distpath pyinstaller/dist --workpath pyinstaller/build --name EV3-IDE main.py
```

---

## Usage

* **C++ Projects:**

  Use `#include <ev3dev.h>` and compile with the built-in button or manually in Terminal with the following command:
    ```bash
    ssh robot@ev3dev.local g++ <input_file> -o <output_file> -lev3dev
    ```
    Or if you don't have or don't want to use `libev3dev.a`:
    ```bash
    ssh robot@ev3dev.local g++ ev3dev.cpp <input_file> -o <output_file>
    ```
* **Python Projects:**

    Use the built-in `ev3dev2` library, for example:
    ```bash
    from ev3dev2.motor import MediumMotor, LargeMotor, OUTPUT_A, OUTPUT_D
    ```
    Get more info at [https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/stable/spec.html](https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/stable/spec.html).
  
---

## Notes

* The IDE creates temporary folders on the EV3 to stage files before moving them to system directories.
* Automatic copying of system files works only after setting up passwordless SSH and `sudo NOPASSWD`.

---

## Disclaimer

This project is provided "as is", without warranty of any kind.  
Use at your own risk.  

The EV3 icon is AI-generated based on inspiration from LEGO EV3 hardware.  
Icons in this project are provided by FlatIcon ([https://www.flaticon.com](https://www.flaticon.com)).  
The IDE uses the JetBrains Mono font, courtesy of JetBrains ([https://www.jetbrains.com/lp/mono/](https://www.jetbrains.com/lp/mono/)).  

LEGO® and LEGO Mindstorms® are trademarks of the LEGO Group.
This project is not affiliated with or endorsed by the LEGO Group.

---

## Contact / Feedback

If you encounter bugs or have suggestions, feel free to contact:

evdev32@gmail.com

---

## License

See LICENSE file for details.
