import customtkinter as ctk

class Settings:
    def __init__(self, root):
        self.root = root
        self.ev3_screen_viewer_toggle_value = 1
        self.syntax_highlighting_enabled = True
        self.syntax_highlighting_var = ctk.StringVar(value="on")

    def open_settings(self, toggle_ev3_screen_viewer, ev3_screen_viewer_toggle_value, toggle_syntax_highlighting):
        # -------- Variablen --------
        self.toggle_ev3_screen_viewer = toggle_ev3_screen_viewer
        self.ev3_screen_viewer_toggle_value = ev3_screen_viewer_toggle_value
        self.toggle_syntax_highlighting = toggle_syntax_highlighting
        # -------- Overlay --------
        self.overlay = ctk.CTkFrame(self.root, fg_color="#1C1A1A")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.settings_frame = ctk.CTkScrollableFrame(self.overlay, width=650, corner_radius=10)
        self.settings_frame.place(relx=0.5, rely=0.5, relheight=900/1009, anchor="center")
        # -------- Status-Updater --------
        self.status_updater_label = ctk.CTkLabel(self.settings_frame, text="Status Updater", text_color="#D4D4D4", font=("Segoe UI", 24, "bold"), fg_color=("gray86", "gray17"), bg_color=("gray86", "gray17"))
        self.status_updater_label.pack()
        self.ev3_screen_viewer_var = ctk.StringVar(value="on")
        self.ev3_screen_viewer_switch = ctk.CTkSwitch(self.settings_frame, text=" EV3 screen viewer", text_color="#D4D4D4", font=("Segoe UI", 14), fg_color="black", bg_color=("gray86", "gray17"), variable=self.ev3_screen_viewer_var, command=lambda: self.toggle(self.ev3_screen_viewer_var.get()), onvalue=1, offvalue=0)
        self.ev3_screen_viewer_switch.pack(padx=10, pady=(8, 20), anchor="nw")
        if int(self.ev3_screen_viewer_toggle_value) == 1:
            self.ev3_screen_viewer_switch.select()
        elif int(self.ev3_screen_viewer_toggle_value) == 0:
            self.ev3_screen_viewer_switch.deselect()
        # -------- Editor --------
        self.editor_label = ctk.CTkLabel(self.settings_frame, text="Editor", text_color="#D4D4D4", font=("Segoe UI", 24, "bold"), fg_color=("gray86", "gray17"), bg_color=("gray86", "gray17"))
        self.editor_label.pack()
        # Syntax-Highlighting
        self.syntax_highlighting_switch = ctk.CTkSwitch(self.settings_frame, text=" Syntax highlighting", text_color="#D4D4D4", font=("Segoe UI", 14), fg_color="black", bg_color=("gray86", "gray17"), command=self.toggle_highlighting, onvalue="on", offvalue="off", variable=self.syntax_highlighting_var)
        self.syntax_highlighting_switch.pack(padx=10, pady=(8, 8), anchor="nw")
        # Python-Snippets
        self.python_snippets_label = ctk.CTkLabel(self.settings_frame, text="Python snippets:", text_color="#D4D4D4", font=("Segoe UI", 14), fg_color=("gray86", "gray17"), bg_color=("gray86", "gray17"))
        self.python_snippets_label.pack(padx=10, pady=(8, 2), anchor="nw")
        self.python_snippets_textbox = ctk.CTkTextbox(self.settings_frame, height=325, width=625, font=("JetBrains Mono", 14), corner_radius=7, text_color="#B5B5B5", wrap="none", fg_color=["gray86", "gray17"], border_width=1, border_color="#474343")
        self.python_snippets_textbox.pack(padx=10, pady=(2, 2), anchor="nw")
        self.python_snippets_textbox.insert("1.0", '!_main   ->   if __name__ == "__main__":\n\t\t   |\n\n!open    ->   with open("|", "r") as f:\n\n!init    ->   def __init__(self, |):\n\n!class   ->   class |:\n\t\t   def __init__(self):\n\t\t        pass\n\n!try     ->   try:\n\t\t   |\n\t      except Exception:\n\t\t   pass\n\n#!       ->   #!/usr/bin/env python3')
        self.python_snippets_textbox.configure(state="disabled")
        # C++-Snippets
        self.cpp_snippets_label = ctk.CTkLabel(self.settings_frame, text="C++ snippets:", text_color="#D4D4D4", font=("Segoe UI", 14), fg_color=("gray86", "gray17"), bg_color=("gray86", "gray17"))
        self.cpp_snippets_label.pack(padx=10, pady=(4, 2), anchor="nw")
        self.cpp_snippets_textbox = ctk.CTkTextbox(self.settings_frame, height=470, width=625, font=("JetBrains Mono", 14), corner_radius=7, text_color="#B5B5B5", wrap="none", fg_color=["gray86", "gray17"], border_width=1, border_color="#474343")
        self.cpp_snippets_textbox.pack(padx=10, pady=(2, 2), anchor="nw")
        self.cpp_snippets_textbox.insert("1.0", '!main    ->   int main()\n\t      {\n\t\t   |\n\t\t   return 0;\n\t      }\n\n!cpp     ->   #include <iostream>\n\t      using namespace std;\n\t      int main()\n\t      {\n\t\t   cout << "|\\n";\n\t\t   return 0;\n\t      }\n\n!inc     ->   #include <|>\n\n!incs    ->   #include <iostream>\n\n!cout    ->   cout << "|\\n";\n\n!cout:   ->   std::cout << "|\\n";\n\n!cin     ->   cin >> |;\n\n!cin:    ->   std::cin >> |;')
        self.cpp_snippets_textbox.configure(state="disabled")
        # Key-Bindings
        self.root.bind("<Escape>", self.close_settings)

    def toggle(self, value):
        self.ev3_screen_viewer_toggle_value = value
        self.toggle_ev3_screen_viewer(value)

    def toggle_highlighting(self, event=None):
        self.syntax_highlighting_enabled = not self.syntax_highlighting_enabled
        self.toggle_syntax_highlighting(self.syntax_highlighting_enabled)

    def close_settings(self, event=None):
        self.root.unbind_all("<Escape>")
        self.overlay.destroy()