import customtkinter as ctk
from tkinter import ttk, messagebox
from database.db_manager import Database
from config.settings import *
from datetime import datetime

class AgendaScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = Database()
        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(header_frame, text="Planning & Échéances", 
                     font=("Segoe UI", 24, "bold"), text_color=COLOR_ACCENT).pack(side="left")

        # Zone principale (Division en 2 : Formulaire à gauche, Tableau à droite)
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30)

        # --- FORMULAIRE D'AJOUT (PANNEAU GAUCHE) ---
        self.setup_form_panel(main_container)

        # --- TABLEAU DES ÉVÉNEMENTS (PANNEAU DROIT) ---
        self.setup_table_panel(main_container)
        
        self.charger_evenements()

    def setup_form_panel(self, parent):
        form_frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD_BG, width=300, corner_radius=15)
        form_frame.pack(side="left", fill="y", padx=(0, 20), pady=10)
        form_frame.pack_propagate(False)

        ctk.CTkLabel(form_frame, text="Nouvel Événement", font=("Segoe UI", 16, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=20)

        self.ent_titre = ctk.CTkEntry(form_frame, placeholder_text="Titre (ex: Vidange Camion)", width=240)
        self.ent_titre.pack(pady=10, padx=20)

        self.ent_date = ctk.CTkEntry(form_frame, placeholder_text="AAAA-MM-JJ", width=240)
        self.ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_date.pack(pady=10, padx=20)

        self.combo_cat = ctk.CTkComboBox(form_frame, values=["Maintenance", "Réunion", "Paie", "Administratif", "Autre"], width=240)
        self.combo_cat.set("Maintenance")
        self.combo_cat.pack(pady=10, padx=20)

        self.combo_prio = ctk.CTkComboBox(form_frame, values=["Haute", "Normale", "Basse"], width=240)
        self.combo_prio.set("Normale")
        self.combo_prio.pack(pady=10, padx=20)

        ctk.CTkButton(form_frame, text="Ajouter à l'agenda", fg_color=COLOR_ACCENT, text_color=COLOR_MAIN_BG,
                     font=("Segoe UI", 13, "bold"), command=self.ajouter_evenement).pack(pady=30, padx=20)

    def setup_table_panel(self, parent):
        table_frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD_BG, corner_radius=15)
        table_frame.pack(side="right", fill="both", expand=True, pady=10)

        # --- CONFIGURATION DU STYLE SOMBRE POUR TREEVIEW ---
        style = ttk.Style()
        style.theme_use("default") # Réinitialise pour appliquer nos couleurs
        
        style.configure("Treeview", 
                        background=COLOR_CARD_BG, 
                        foreground=COLOR_TEXT_MAIN, 
                        fieldbackground=COLOR_CARD_BG, 
                        borderwidth=0, 
                        rowheight=35,
                        font=("Segoe UI", 10))
        
        style.configure("Treeview.Heading", 
                        background=COLOR_SIDEBAR, 
                        foreground=COLOR_ACCENT, 
                        relief="flat",
                        font=("Segoe UI", 11, "bold"))

        style.map("Treeview", background=[('selected', COLOR_ACCENT)], foreground=[('selected', COLOR_MAIN_BG)])

        cols = ("ID", "DATE", "ÉVÉNEMENT", "TYPE", "PRIORITÉ", "STATUT")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="Treeview")
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        self.tree.pack(fill="both", expand=True, padx=15, pady=15)

        # Actions sous le tableau
        actions = ctk.CTkFrame(table_frame, fg_color="transparent")
        actions.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(actions, text="Marquer Terminé", fg_color="#10B981", height=32, command=self.terminer_event).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Supprimer", fg_color=COLOR_ERROR, height=32, command=self.supprimer_event).pack(side="right", padx=5)

    def ajouter_evenement(self):
        titre, date_e, cat, prio = self.ent_titre.get(), self.ent_date.get(), self.combo_cat.get(), self.combo_prio.get()

        if titre and date_e:
            self.db.query("INSERT INTO agenda (titre, date_event, categorie, priorite) VALUES (?,?,?,?)",
                          (titre, date_e, cat, prio))
            messagebox.showinfo("Succès", "Événement ajouté au planning.")
            self.ent_titre.delete(0, 'end')
            self.charger_evenements()
        else:
            messagebox.showwarning("Erreur", "Veuillez remplir le titre et la date.")

    def charger_evenements(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        rows = self.db.query("SELECT id, date_event, titre, categorie, priorite, statut FROM agenda ORDER BY date_event ASC").fetchall()
        for r in rows:
            self.tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], r[5]))

    def terminer_event(self):
        selected = self.tree.selection()
        if selected:
            item_id = self.tree.item(selected[0])['values'][0]
            self.db.query("UPDATE agenda SET statut = 'Terminé' WHERE id = ?", (item_id,))
            self.charger_evenements()

    def supprimer_event(self):
        selected = self.tree.selection()
        if selected:
            item_id = self.tree.item(selected[0])['values'][0]
            if messagebox.askyesno("Confirmation", "Supprimer cet événement ?"):
                self.db.query("DELETE FROM agenda WHERE id = ?", (item_id,))
                self.charger_evenements()