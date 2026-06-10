import customtkinter as ctk
import numpy as np
from PIL import Image, ImageTk
from ev3_sender import EV3Sender
import threading
import time

class StatusUpdater:
    def __init__(self, root, ssh_container):
        # -------- Variablen --------
        self.root = root
        self.ssh_container = ssh_container
        self.ev3_sender = EV3Sender(ssh_container)
        self.EV3_HEIGHT = 128
        self.EV3_WIDTH = 178
        self.PIXEL_SIZE = 1
        self.base_frame_location_x = 5
        self.base_frame_location_y = 80
        self.activated_color = "#BFCFF2"
        self.deactivated_color = "gray"
        self.deactivated_text = "---"
        self.alive_running = False
        self.alive_thread_object = None
        # -------- GUI-Elemente --------
        # Hintergrund-Frame
        self.device_status_frame = ctk.CTkFrame(self.root, height=295, width=587, corner_radius=7, fg_color="#1C1A1A")
        self.device_status_frame.place(x=self.base_frame_location_x, y=self.base_frame_location_y)
        # EV3-Screen-Viewer
        self.screen_canvas = ctk.CTkCanvas(self.device_status_frame, height=self.EV3_HEIGHT * self.PIXEL_SIZE, width=self.EV3_WIDTH * self.PIXEL_SIZE, bg=f"#{120:02x}{120:02x}{120:02x}", highlightthickness=0)
        self.screen_canvas.place(x=13, y=13)
        # EV3-Frame
        self.ev3_bottom_part_frame = ctk.CTkFrame(self.device_status_frame, height=self.EV3_HEIGHT * self.PIXEL_SIZE + 10, width=self.EV3_WIDTH * self.PIXEL_SIZE, fg_color=f"#{140:02x}{140:02x}{140:02x}", corner_radius=0)
        self.ev3_bottom_part_frame.place(x=13, y=142)
        # EV3-Buttons
        img = Image.open("images/arrow.png").resize((24, 24), Image.Resampling.LANCZOS).rotate(90, expand=True)
        self.ev3_up_button = ctk.CTkButton(self.device_status_frame, text="", width=1, height=1, fg_color="#707070", text_color="black", hover_color="#c0c0c0", image=ctk.CTkImage(light_image=img, dark_image=img, size=(24, 24)), corner_radius=0, command=lambda: self.ev3_sender.send_message("BUTTON up"))
        self.ev3_up_button.place(x=84, y=158)
        img = Image.open("images/arrow.png").resize((24, 24), Image.Resampling.LANCZOS).rotate(-90, expand=True)
        self.ev3_down_button = ctk.CTkButton(self.device_status_frame, text="", width=1, height=1, fg_color="#707070", text_color="black", hover_color="#c0c0c0", image=ctk.CTkImage(light_image=img, dark_image=img, size=(24, 24)), corner_radius=0, command=lambda: self.ev3_sender.send_message("BUTTON down"))
        self.ev3_down_button.place(x=84, y=232)
        img = Image.open("images/arrow.png").resize((24, 24), Image.Resampling.LANCZOS)
        self.ev3_right_button = ctk.CTkButton(self.device_status_frame, text="", width=1, height=1, fg_color="#707070", text_color="black", hover_color="#c0c0c0", image=ctk.CTkImage(light_image=img, dark_image=img, size=(24, 24)), corner_radius=0, command=lambda: self.ev3_sender.send_message("BUTTON right"))
        self.ev3_right_button.place(x=121, y=195)
        img = Image.open("images/arrow.png").resize((24, 24), Image.Resampling.LANCZOS).rotate(180, expand=True)
        self.ev3_left_button = ctk.CTkButton(self.device_status_frame, text="", width=1, height=1, fg_color="#707070", text_color="black", hover_color="#c0c0c0", image=ctk.CTkImage(light_image=img, dark_image=img, size=(24, 24)), corner_radius=0, command=lambda: self.ev3_sender.send_message("BUTTON left"))
        self.ev3_left_button.place(x=47, y=195)
        self.ev3_enter_button = ctk.CTkButton(self.device_status_frame, text="", width=32, height=32, fg_color="#797979", text_color="black", hover_color="#c0c0c0", corner_radius=0, command=lambda: self.ev3_sender.send_message("BUTTON enter"))
        self.ev3_enter_button.place(x=84, y=195)
        self.ev3_backspace_button = ctk.CTkButton(self.device_status_frame, text="", width=39, height=19, fg_color="#707070", bg_color="#707070", text_color="black", hover_color="#c0c0c0", corner_radius=0, command=lambda: self.ev3_sender.send_message("BUTTON backspace"), border_width=0, border_color="#707070", )
        self.ev3_backspace_button.place(x=22, y=142)
        # Motor-Anzeige
        self.output_a_label = ctk.CTkLabel(self.device_status_frame, text="Output A:", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.output_a_label.place(x=235, y=13)
        self.output_a_device_label = ctk.CTkLabel(self.device_status_frame, text=self.deactivated_text, font=("Segoe UI", 12), text_color=self.deactivated_color, fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.output_a_device_label.place(x=296, y=13)
        self.output_b_label = ctk.CTkLabel(self.device_status_frame, text="Output B:", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.output_b_label.place(x=400, y=13)
        self.output_b_device_label = ctk.CTkLabel(self.device_status_frame, text=self.deactivated_text, font=("Segoe UI", 12), text_color=self.deactivated_color, fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.output_b_device_label.place(x=461, y=13)
        self.output_c_label = ctk.CTkLabel(self.device_status_frame, text="Output C:", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.output_c_label.place(x=235, y=50)
        self.output_c_device_label = ctk.CTkLabel(self.device_status_frame, text=self.deactivated_text, font=("Segoe UI", 12), text_color=self.deactivated_color, fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.output_c_device_label.place(x=296, y=50)
        self.output_d_label = ctk.CTkLabel(self.device_status_frame, text="Output D:", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.output_d_label.place(x=400, y=50)
        self.output_d_device_label = ctk.CTkLabel(self.device_status_frame, text=self.deactivated_text, font=("Segoe UI", 12), text_color=self.deactivated_color, fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.output_d_device_label.place(x=461, y=50)
        # Trennstrich 1
        self.line_1 = ctk.CTkFrame(self.device_status_frame, height=2, width=330, fg_color="#3A3A3A", bg_color="#3A3A3A", border_color="#3A3A3A")
        self.line_1.place(x=225, y=88)
        # Sensor-Anzeige
        self.input_1_label = ctk.CTkLabel(self.device_status_frame, text="Input 1:", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.input_1_label.place(x=235, y=101)
        self.input_1_device_label = ctk.CTkLabel(self.device_status_frame, text=self.deactivated_text, font=("Segoe UI", 12), text_color=self.deactivated_color, fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.input_1_device_label.place(x=284, y=101)
        self.input_2_label = ctk.CTkLabel(self.device_status_frame, text="Input 2:", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.input_2_label.place(x=400, y=101)
        self.input_2_device_label = ctk.CTkLabel(self.device_status_frame, text=self.deactivated_text, font=("Segoe UI", 12), text_color=self.deactivated_color, fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.input_2_device_label.place(x=449, y=101)
        self.input_3_label = ctk.CTkLabel(self.device_status_frame, text="Input 3:", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.input_3_label.place(x=235, y=138)
        self.input_3_device_label = ctk.CTkLabel(self.device_status_frame, text=self.deactivated_text, font=("Segoe UI", 12), text_color=self.deactivated_color, fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.input_3_device_label.place(x=284, y=138)
        self.input_4_label = ctk.CTkLabel(self.device_status_frame, text="Input 4:", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.input_4_label.place(x=400, y=138)
        self.input_4_device_label = ctk.CTkLabel(self.device_status_frame, text=self.deactivated_text, font=("Segoe UI", 12), text_color=self.deactivated_color, fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.input_4_device_label.place(x=449, y=138)
        # Trennstrich 2
        self.line_2 = ctk.CTkFrame(self.device_status_frame, height=2, width=330, fg_color="#3A3A3A", bg_color="#3A3A3A", border_color="#3A3A3A")
        self.line_2.place(x=225, y=176)
        # Batterie-Anzeige
        self.battery_voltage_label = ctk.CTkLabel(self.device_status_frame, text="Battery voltage:", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.battery_voltage_label.place(x=235, y=189)
        self.battery_voltage_value_label = ctk.CTkLabel(self.device_status_frame, text=self.deactivated_text, font=("Segoe UI", 12), text_color=self.deactivated_color, fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.battery_voltage_value_label.place(x=539, y=189, anchor="ne")
        self.battery_percent_label = ctk.CTkLabel(self.device_status_frame, text="Battery percentage:", font=("Segoe UI", 12), text_color="#D4D4D4", fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.battery_percent_label.place(x=235, y=226)
        self.battery_percent_value_label = ctk.CTkLabel(self.device_status_frame, text=self.deactivated_text, font=("Segoe UI", 12), text_color=self.deactivated_color, fg_color="#1C1A1A", bg_color="#1C1A1A")
        self.battery_percent_value_label.place(x=539, y=226, anchor="ne")
        # ------- Motor-Dicts --------
        self.motor_to_name_dict = {"lego-ev3-l-motor": "LargeMotor", "lego-ev3-m-motor": "MediumMotor"}
        self.output_to_label_dict = {"ev3-ports:outA": self.output_a_device_label, "ev3-ports:outB": self.output_b_device_label, "ev3-ports:outC": self.output_c_device_label, "ev3-ports:outD": self.output_d_device_label,}
        self.sensor_to_name_dict = {"lego-ev3-touch": "TouchSensor", "lego-ev3-color": "ColorSensor", "lego-ev3-us": "UltrasonicSensor", "lego-ev3-gyro": "GyroSensor", "lego-ev3-ir": "InfraredSensor", "lego-nxt-touch": "TouchSensor [NXT]", "lego-nxt-light": "LightSensor [NXT]", "lego-nxt-color": "ColorSensor [NXT]", "lego-nxt-us": "UltrasonicSensor [N]", "lego-nxt-temp": "TemperatureSensor [N]", "lego-nxt-sound": "SoundSensor [NXT]"}
        self.input_to_label_dict = {"ev3-ports:in1": self.input_1_device_label, "ev3-ports:in2": self.input_2_device_label, "ev3-ports:in3": self.input_3_device_label, "ev3-ports:in4": self.input_4_device_label}

    def show_connected(self, device_name):
        if not self.alive_running:
            self.alive_running = True
            self.alive_thread_object = threading.Thread(target=self.alive_thread, daemon=True)
            self.alive_thread_object.start()

    def alive_thread(self):
        while self.alive_running:
            try:
                self.ev3_sender.send_message("INFO active")
            except Exception:
                break
            time.sleep(1)

    def show_disconnected(self):
        self.alive_running = False
        self.screen_canvas.delete("all")
        self.screen_canvas.create_text(86, 62, text="?", font=("Arial", 40), fill="black")
        self.output_a_device_label.configure(text=self.deactivated_text, text_color=self.deactivated_color)
        self.output_b_device_label.configure(text=self.deactivated_text, text_color=self.deactivated_color)
        self.output_c_device_label.configure(text=self.deactivated_text, text_color=self.deactivated_color)
        self.output_d_device_label.configure(text=self.deactivated_text, text_color=self.deactivated_color)
        self.input_1_device_label.configure(text=self.deactivated_text, text_color=self.deactivated_color)
        self.input_2_device_label.configure(text=self.deactivated_text, text_color=self.deactivated_color)
        self.input_3_device_label.configure(text=self.deactivated_text, text_color=self.deactivated_color)
        self.input_4_device_label.configure(text=self.deactivated_text, text_color=self.deactivated_color)
        self.battery_voltage_value_label.configure(text=self.deactivated_text, text_color=self.deactivated_color)
        self.battery_percent_value_label.configure(text=self.deactivated_text, text_color=self.deactivated_color)

    def update_screen(self, content):
        self.draw_screen(self.bits_to_pixels(content))

    def bits_to_pixels(self, bits):
        try:
            pixels = [[0] * self.EV3_WIDTH for _ in range(self.EV3_HEIGHT)]
            idx = 0
            for y in range(self.EV3_HEIGHT):
                for x in range(self.EV3_WIDTH):
                    pixels[y][x] = bits[idx + 2]
                    idx += 4
            return pixels
        except Exception:
            return

    def draw_screen(self, pixels):
        try:
            arr = np.array(pixels, dtype=np.uint8)
            arr = (arr / 255.0 * 120).astype(np.uint8) # Werte skalieren
            img = Image.fromarray(arr, mode='L')
            img = img.resize((self.EV3_WIDTH * self.PIXEL_SIZE, self.EV3_HEIGHT * self.PIXEL_SIZE), Image.NEAREST)
            self.tk_image = ImageTk.PhotoImage(img)
            self.screen_canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        except Exception:
            return

    def update_battery(self, voltage_now, voltage_min, voltage_max):
        voltage_now = round(voltage_now / 1000000, 2)
        voltage_min = round(voltage_min / 10000000, 2)
        voltage_max = round(voltage_max / 10000000, 2)
        battery_percentage = (voltage_now - voltage_min) / (voltage_max - voltage_min) * 100
        battery_percentage = min(max(battery_percentage, 0), 100)
        self.battery_voltage_value_label.configure(text=f"{voltage_now} V", text_color=self.activated_color)
        self.battery_percent_value_label.configure(text=f"{battery_percentage:.0f} %", text_color=self.activated_color)

    def update_motors(self, motor_dict):
        existing_ports = ["ev3-ports:outA", "ev3-ports:outB", "ev3-ports:outC", "ev3-ports:outD"]
        for address, motor in motor_dict.items():
            label = self.output_to_label_dict[address]
            try:
                motor_name = self.motor_to_name_dict[motor]
            except Exception:
                motor_name = "UnknownMotor"
            label.configure(text=motor_name, text_color=self.activated_color)
            try:
                existing_ports.remove(address)
            except Exception:
                pass
        for free_port in existing_ports:
            label = self.output_to_label_dict[free_port]
            label.configure(text=f"{self.deactivated_text}", text_color=self.deactivated_color)

    def update_sensors(self, sensor_dict):
        existing_ports = ["ev3-ports:in1", "ev3-ports:in2", "ev3-ports:in3", "ev3-ports:in4"]
        for address, sensor in sensor_dict.items():
            label = self.input_to_label_dict[address[0:13]]
            try:
                sensor_name = self.sensor_to_name_dict[sensor]
            except Exception:
                sensor_name = "UnknownSensor"
            label.configure(text=sensor_name, text_color=self.activated_color)
            try:
                existing_ports.remove(address[0:13])
            except Exception:
                pass
        for free_port in existing_ports:
            label = self.input_to_label_dict[free_port]
            label.configure(text=f"{self.deactivated_text}", text_color=self.deactivated_color)

    def hide_all_elements(self):
        self.device_status_frame.place_forget()

    def show_all_elements(self):
        self.device_status_frame.place(x=self.base_frame_location_x, y=self.base_frame_location_y)