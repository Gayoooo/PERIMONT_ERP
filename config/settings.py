import os
import sys

# --- FONCTION DE DÉTECTION DES CHEMINS (INDISPENSABLE POUR EXE) ---
def get_resource_path(relative_path):
    """ Récupère le chemin absolu des ressources pour PyInstaller """
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # En mode développement, on utilise le chemin normal
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- CHEMINS ---
# On utilise get_resource_path pour que l'EXE ne crash pas
BASE_DIR = get_resource_path("")
DB_PATH = get_resource_path(os.path.join("database", "perimont.db"))

# --- DESIGN SYSTEM ULTRA MODERNE ---
COLOR_MAIN_BG = "#0F172A"      
COLOR_CARD_BG = "#1E293B"      
COLOR_ACCENT = "#38BDF8"       
COLOR_TEXT_MAIN = "#F8FAFC"    
COLOR_TEXT_DIM = "#94A3B8"     
COLOR_ERROR = "#F87171"        
COLOR_SIDEBAR = "#020617" 

# --- DIMENSIONS ---
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
VERSION = "1.2"

# --- INFORMATIONS DE LA SOCIÉTÉ ---
COMPANY_NAME = "PERIMONT SAS"
COMPANY_ADDRESS = "Rex, Grand Marché, vers Pressing Fatia"
COMPANY_CITY = "Pointe-Noire, Congo"
COMPANY_PHONE = "+242 05 025 26 26 / +242 05 307 77 73"
COMPANY_STATUT = "SA au capital de 10 000 000 CFA"
COMPANY_NIF = "RCCM: CG-BZV-2023-B16-00003"

# --- LOGO CORRIGÉ ---
COMPANY_LOGO = get_resource_path(os.path.join("assets", "logo.png"))