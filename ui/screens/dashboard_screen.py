import customtkinter as ctk
from database.db_manager import Database
from config.settings import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = Database()
        self.fig = None 
        self.setup_ui()

    def setup_ui(self):
        # --- TITRE ---
        ctk.CTkLabel(self, text="Tableau de Bord Général", 
                     font=("Segoe UI", 24, "bold"), text_color=COLOR_ACCENT).pack(pady=20, anchor="w", padx=30)

        # --- RÉCUPÉRATION DES DONNÉES ---
        nb_emp = self.db.query("SELECT COUNT(*) as count FROM personnel").fetchone()['count']
        nb_cam = self.db.query("SELECT COUNT(*) as count FROM camions").fetchone()['count']
        
        # Données Agenda
        today = datetime.now().strftime("%Y-%m-%d")
        nb_agenda = self.db.query("SELECT COUNT(*) as count FROM agenda WHERE statut != 'Terminé'").fetchone()['count']
        events_today = self.db.query("SELECT titre, priorite FROM agenda WHERE date_event = ? AND statut != 'Terminé'", (today,)).fetchall()

        # Données Finances
        res_fin = self.db.query("SELECT type, SUM(montant) as total FROM finances GROUP BY type").fetchall()
        entrees = sum(r['total'] for r in res_fin if r['type'] == 'ENTRÉE')
        sorties = sum(r['total'] for r in res_fin if r['type'] == 'SORTIE')
        solde = entrees - sorties

        # --- GRILLE DE STATISTIQUES (Passage à 4 colonnes pour l'agenda) ---
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20)
        
        self.create_stat_card("EMPLOYÉS", nb_emp, 0, 0, "#3B82F6")
        self.create_stat_card("CAMIONS", nb_cam, 0, 1, "#F59E0B")
        self.create_stat_card("SOLDE CAISSE", f"{solde:,.0f} F", 0, 2, "#10B981")
        self.create_stat_card("À FAIRE (AGENDA)", nb_agenda, 0, 3, COLOR_ACCENT)

        # --- ZONE BASSE ---
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Graphique (Gauche)
        self.chart_frame = ctk.CTkFrame(self.bottom_frame, fg_color=COLOR_CARD_BG, corner_radius=15)
        self.chart_frame.pack(side="left", fill="both", expand=True, padx=10)
        self.create_finance_chart(entrees, sorties)

        # Panneau latéral Alertes & Planning (Droite)
        self.right_panel = ctk.CTkFrame(self.bottom_frame, fg_color="transparent", width=300)
        self.right_panel.pack(side="right", fill="both", padx=10)

        # 1. Alertes Stocks
        self.alert_frame = ctk.CTkFrame(self.right_panel, fg_color=COLOR_CARD_BG, corner_radius=15, height=200)
        self.alert_frame.pack(fill="x", pady=(0, 10))
        self.show_stock_alerts()

        # 2. Échéances du Jour (Nouveau !)
        self.agenda_mini_frame = ctk.CTkFrame(self.right_panel, fg_color=COLOR_CARD_BG, corner_radius=15)
        self.agenda_mini_frame.pack(fill="both", expand=True)
        self.show_today_planning(events_today)

    def create_stat_card(self, title, value, row, col, color):
        card = ctk.CTkFrame(self.stats_frame, fg_color=COLOR_CARD_BG, width=220, height=120, corner_radius=15)
        card.grid(row=row, column=col, padx=10, pady=10)
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_DIM).pack(pady=(20, 5))
        ctk.CTkLabel(card, text=str(value), font=("Segoe UI", 24, "bold"), text_color=color).pack()

    def show_today_planning(self, events):
        ctk.CTkLabel(self.agenda_mini_frame, text="📅 AUJOURD'HUI", font=("Segoe UI", 14, "bold"), text_color=COLOR_ACCENT).pack(pady=10)
        if not events:
            ctk.CTkLabel(self.agenda_mini_frame, text="Rien de prévu ✅", text_color=COLOR_TEXT_DIM).pack(pady=20)
        else:
            for ev in events:
                color = "#F87171" if ev['priorite'] == "Haute" else COLOR_TEXT_MAIN
                prefix = "🔴" if ev['priorite'] == "Haute" else "🔹"
                msg = f"{prefix} {ev['titre']}"
                ctk.CTkLabel(self.agenda_mini_frame, text=msg, text_color=color, font=("Segoe UI", 12), wraplength=250).pack(anchor="w", padx=20, pady=5)

    def create_finance_chart(self, in_val, out_val):
        ctk.CTkLabel(self.chart_frame, text="Répartition Entrées / Sorties", font=("Segoe UI", 14, "bold")).pack(pady=10)
        if self.fig: plt.close(self.fig)
        self.fig, ax = plt.subplots(figsize=(4, 3), facecolor='#1e293b')
        ax.set_facecolor('#1e293b')
        labels = ['Entrées', 'Sorties']
        sizes = [max(in_val, 1), max(out_val, 1)]
        colors = ['#10B981', '#EF4444']
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, textprops={'color':"w", 'weight':'bold'})
        ax.axis('equal')
        canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def show_stock_alerts(self):
        ctk.CTkLabel(self.alert_frame, text="⚠️ ALERTES STOCKS", font=("Segoe UI", 14, "bold"), text_color="#EF4444").pack(pady=10)
        alerts = self.db.query("SELECT nom_article, quantite, seuil_alerte FROM stock WHERE quantite <= seuil_alerte").fetchall()
        if not alerts:
            ctk.CTkLabel(self.alert_frame, text="Stocks OK ✅", text_color="#10B981").pack(pady=10)
        else:
            for art in alerts:
                msg = f"• {art['nom_article']} : {art['quantite']}"
                ctk.CTkLabel(self.alert_frame, text=msg, text_color="#F87171", font=("Segoe UI", 11)).pack(anchor="w", padx=20)

    def destroy(self):
        if self.fig: plt.close(self.fig)
        super().destroy()