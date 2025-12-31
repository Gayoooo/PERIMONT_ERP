#ui/screens/main_window.py

import customtkinter as ctk
from config.settings import *
from datetime import datetime
from PIL import Image

# Importation des écrans
from ui.screens.personnel_screen import PersonnelScreen
from ui.screens.paie_screen import PaieScreen
from ui.screens.logistique_screen import LogistiqueScreen
from ui.screens.dashboard_screen import DashboardScreen
from ui.screens.agenda_screen import AgendaScreen
from ui.screens.stock_screen import StockScreen # Import
from ui.screens.finances_screen import FinancesScreen # Import

class MainWindow(ctk.CTkFrame):
    def __init__(self, parent, user_data):
        super().__init__(parent, fg_color=COLOR_MAIN_BG)
        self.user_data = user_data

        # Configuration de la grille (Colonne 0: Menu, Colonne 1: Contenu)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- BARRE LATÉRALE (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=240, fg_color=COLOR_CARD_BG, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

       # --- BRANDING (LOGO) ---
        try:
            # On charge l'image
            logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
            img = Image.open(logo_path)
            
            # On crée l'objet CTkImage (ajuste les tailles 150, 50 selon ton image)
            self.logo_image = ctk.CTkImage(light_image=img, dark_image=img, size=(180, 60))
            
            # On affiche l'image dans un label
            self.logo_label = ctk.CTkLabel(self.sidebar, image=self.logo_image, text="")
            self.logo_label.pack(pady=(30, 40), padx=20)
        except Exception as e:
            # Si l'image est introuvable, on remet le texte par défaut
            print(f"Erreur chargement logo : {e}")
            self.logo_label = ctk.CTkLabel(self.sidebar, text="PERIMONT ERP", 
                                          font=("Segoe UI", 22, "bold"), text_color=COLOR_ACCENT)
            self.logo_label.pack(pady=(30, 40), padx=20)

        # Définition des modules de navigation
        # Structure : (Texte Bouton, ID, Classe de l'écran)
        self.menu_items = [
            ("Tableau de bord", "dashboard", DashboardScreen),
            ("Personnel", "personnel", PersonnelScreen),
            ("Paie & Salaires", "paie", PaieScreen),
            ("Logistique", "logistique", LogistiqueScreen),
            ("Stocks & Carburant", "stock", StockScreen),
            ("Finances", "finances", FinancesScreen),
            ("Agenda", "agenda", AgendaScreen)
        ]

        self.nav_buttons = {}
        for text, name, screen_class in self.menu_items:
            self.create_nav_button(text, name, screen_class)

        # --- ZONE DE CONTENU PRINCIPALE ---
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=25, pady=20)

        # --- BARRE SUPÉRIEURE (HEADER) ---
        self.header = ctk.CTkFrame(self.content_area, fg_color=COLOR_CARD_BG, height=70, corner_radius=15)
        self.header.pack(fill="x", pady=(0, 25))
        self.header.pack_propagate(False)
        
        # Horloge dynamique
        self.clock_label = ctk.CTkLabel(self.header, text="", font=("Segoe UI", 16, "bold"), text_color=COLOR_TEXT_MAIN)
        self.clock_label.pack(side="left", padx=25)
        
        # Profil utilisateur
        user_display = f"👤 {user_data['username'].upper()}  •  {user_data['role']}"
        self.user_label = ctk.CTkLabel(self.header, text=user_display, 
                                       font=("Segoe UI", 13), text_color=COLOR_TEXT_DIM)
        self.user_label.pack(side="right", padx=25)

        # Initialisation de l'horloge
        self.update_clock()
        
        # Écran par défaut au démarrage : Personnel
        self.after(100, lambda: self.switch_screen(PersonnelScreen))

    def create_nav_button(self, text, name, screen_class):
        """Crée un bouton de navigation stylisé dans la sidebar."""
        btn = ctk.CTkButton(
            self.sidebar, 
            text=f"  {text}", 
            height=50, 
            fg_color="transparent", 
            text_color=COLOR_TEXT_MAIN, 
            anchor="w", 
            hover_color=COLOR_MAIN_BG,
            font=("Segoe UI", 14),
            corner_radius=10,
            command=lambda: self.switch_screen(screen_class) if screen_class else self.show_placeholder(text)
        )
        btn.pack(fill="x", padx=15, pady=5)
        self.nav_buttons[name] = btn

    def switch_screen(self, screen_class):
        """Détruit le contenu actuel et affiche le nouvel écran sélectionné."""
        if screen_class is None:
            return

        # Nettoyage de la zone (on garde le header)
        for widget in self.content_area.winfo_children():
            if widget != self.header:
                widget.destroy()
        
        # Chargement de l'écran
        try:
            new_screen = screen_class(self.content_area)
            new_screen.pack(fill="both", expand=True)
            print(f"Navigation : {screen_class.__name__} chargé.")
        except Exception as e:
            print(f"Erreur lors du chargement de l'écran : {e}")

    def show_placeholder(self, module_name):
        """Affiche un message temporaire pour les modules non encore développés."""
        for widget in self.content_area.winfo_children():
            if widget != self.header:
                widget.destroy()
        
        placeholder = ctk.CTkLabel(self.content_area, 
                                   text=f"Le module '{module_name}' est en cours de développement.", 
                                   font=("Segoe UI", 18, "italic"), text_color=COLOR_TEXT_DIM)
        placeholder.pack(expand=True)

    def update_clock(self):
        """Met à jour l'heure système chaque seconde."""
        now = datetime.now().strftime("%H:%M:%S  |  %d %b %Y")
        self.clock_label.configure(text=now)
        self.after(1000, self.update_clock)