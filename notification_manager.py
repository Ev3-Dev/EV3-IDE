import customtkinter as ctk

class NotificationManager:
    def __init__(self):
        self.active_notifications = []
        self.FRAME_HEIGHT = 100
        self.FRAME_WIDTH = 280

    def show_message(self, root, header, content, duration=4000, margin=20):
        root.update_idletasks()
        # ---- Frame erstellen ----
        notif_frame = ctk.CTkFrame(root, height=self.FRAME_HEIGHT, width=self.FRAME_WIDTH, corner_radius=8, fg_color="#333333", bg_color="#1C1A1A", border_width=1, border_color="#DDDDDD" if header != "Error" else "#FF5A5A")
        notif_frame.pack_propagate(False)
        header_label = ctk.CTkLabel(notif_frame, font=("Segoe UI", 18, "bold"), text=header, text_color="#FFFFFF")
        header_label.pack(pady=(5,0))
        content_label = ctk.CTkLabel(notif_frame, font=("Segoe UI", 13), text=content, text_color="#DDDDDD")
        content_label.pack(pady=(3,5))

        # ---- Startposition (rechts außerhalb des Fensters) ----
        x_start = root.winfo_width()  # Start rechts außerhalb
        y = root.winfo_height() - self.FRAME_HEIGHT - margin - len(self.active_notifications) * (self.FRAME_HEIGHT + 10)
        notif_frame.place(x=x_start, y=y)

        self.active_notifications.append(notif_frame)

        # ---- Animation einblenden ----
        target_x = root.winfo_width() - self.FRAME_WIDTH - margin
        self._slide_in(notif_frame, target_x=target_x, step=10, delay=10)

        # ---- Automatisches Ausblenden nach "duration" ms ----
        root.after(duration, lambda: self._slide_out(notif_frame, step=10, delay=10, margin=margin))

    def _slide_in(self, frame, target_x, step=10, delay=10):
        x = frame.winfo_x()
        if x > target_x:
            x -= step
            frame.place(x=x)
            frame.after(delay, lambda: self._slide_in(frame, target_x, step, delay))
        else:
            frame.place(x=target_x)

    def _slide_out(self, frame, step=10, delay=10, margin=10):
        x = frame.winfo_x()
        root_width = frame.master.winfo_width()
        if x < root_width:
            x += step
            frame.place(x=x)
            frame.after(delay, lambda: self._slide_out(frame, step, delay, margin))
        else:
            frame.destroy()
            if frame in self.active_notifications:
                self.active_notifications.remove(frame)
