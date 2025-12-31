import customtkinter as ctk
import sys
from config.settings import *
from ui.screens.login_screen import LoginScreen
from ui.screens.main_window import MainWindow 

class PerimontERP(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PERIMONT ERP v1.0")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(fg_color=COLOR_MAIN_BG)

        # Protocole de fermeture propre pour éviter les instances fantômes
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.show_login()

    def show_login(self):
        self.login_frame = LoginScreen(self, self.on_login_success)
        self.login_frame.pack(expand=True, fill="both")

    def on_login_success(self, user_data):
        print(f"Connexion réussie : {user_data['username']}")
        self.login_frame.destroy()
        self.main_window = MainWindow(self, user_data)
        self.main_window.pack(expand=True, fill="both")

    def on_closing(self):
        """Ferme proprement l'application et tous les threads."""
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = PerimontERP()
    app.mainloop()