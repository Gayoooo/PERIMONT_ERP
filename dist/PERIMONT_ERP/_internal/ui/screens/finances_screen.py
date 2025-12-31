import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import os
from datetime import datetime
from database.db_manager import Database
from config.settings import *
from utils.pdf_generator import generer_journal_caisse_pdf

class FinancesScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = Database()
        self.editing_id = None
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="Gestion & Bilans Financiers", 
                     font=("Segoe UI", 24, "bold"), text_color=COLOR_ACCENT).pack(pady=20, padx=30, anchor="w")

        # --- RÉSUMÉ VISUEL ---
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.pack(fill="x", padx=30, pady=10)
        self.card_in = self.create_fin_card("ENTRÉES DU MOIS", "0 FCFA", 0, 0, "#10B981")
        self.card_out = self.create_fin_card("SORTIES DU MOIS", "0 FCFA", 0, 1, "#F87171")
        self.card_solde = self.create_fin_card("SOLDE ACTUEL", "0 FCFA", 0, 2, COLOR_ACCENT)

        # --- FORMULAIRE ---
        self.f_box = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=15)
        self.f_box.pack(fill="x", padx=30, pady=15)
        self.ent_lib = ctk.CTkEntry(self.f_box, placeholder_text="Libellé", width=250)
        self.ent_lib.pack(side="left", padx=15, pady=20)
        self.ent_mt = ctk.CTkEntry(self.f_box, placeholder_text="Montant", width=120)
        self.ent_mt.pack(side="left", padx=10, pady=20)
        self.type_var = ctk.StringVar(value="ENTRÉE")
        self.opt_type = ctk.CTkOptionMenu(self.f_box, values=["ENTRÉE", "SORTIE"], variable=self.type_var)
        self.opt_type.pack(side="left", padx=10)
        ctk.CTkButton(self.f_box, text="ENREGISTRER", command=self.sauvegarder, fg_color=COLOR_ACCENT).pack(side="left", padx=15)

        # --- ACTIONS ---
        self.action_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.action_bar.pack(fill="x", padx=30, pady=5)
        ctk.CTkButton(self.action_bar, text="📅 JOURNAL DU JOUR", fg_color="#10B981", command=self.export_journal_jour).pack(side="right", padx=5)
        ctk.CTkButton(self.action_bar, text="📊 BILAN MENSUEL", fg_color="#F59E0B", command=self.export_bilan_mensuel).pack(side="right", padx=5)

        # --- TABLEAU ---
        self.tree = ttk.Treeview(self, columns=("id", "date", "lib", "mt", "tp"), show="headings")
        for col, head in zip(self.tree["columns"], ["ID", "DATE", "LIBELLÉ", "MONTANT", "TYPE"]):
            self.tree.heading(col, text=head)
        self.tree.column("id", width=0, stretch=False)
        self.tree.pack(fill="both", expand=True, padx=30, pady=10)
        self.refresh()

    def create_fin_card(self, title, value, row, col, color):
        card = ctk.CTkFrame(self.summary_frame, fg_color=COLOR_CARD_BG, width=280, height=90, corner_radius=12)
        card.grid(row=row, column=col, padx=10); card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 11)).pack(pady=(10, 0))
        lbl = ctk.CTkLabel(card, text=value, font=("Segoe UI", 18, "bold"), text_color=color)
        lbl.pack(); return lbl

    def export_journal_jour(self):
        date_input = simpledialog.askstring("Date", "Date (AAAA-MM-JJ) :", initialvalue=datetime.now().strftime("%Y-%m-%d"))
        if not date_input: return
        rows = self.db.query("SELECT date, libelle, type, montant FROM finances WHERE date LIKE ?", (f"{date_input}%",)).fetchall()
        if rows:
            data = [[r[0], r[1], r[2], r[3]] for r in rows]
            path = generer_journal_caisse_pdf(data, date_input, titre="JOURNAL DE CAISSE DU JOUR")
            # Correctif : Utilisation du chemin absolu pour os.startfile
            full_path = os.path.abspath(path)
            if os.path.exists(full_path):
                os.startfile(full_path)
            else:
                messagebox.showerror("Erreur", "Le fichier n'a pas pu être créé.")

    def export_bilan_mensuel(self):
        mois_input = simpledialog.askstring("Mois", "Mois (AAAA-MM) :", initialvalue=datetime.now().strftime("%Y-%m"))
        if not mois_input: return
        rows = self.db.query("SELECT date, libelle, type, montant FROM finances WHERE date LIKE ?", (f"{mois_input}%",)).fetchall()
        if rows:
            data = [[r[0], r[1], r[2], r[3]] for r in rows]
            path = generer_journal_caisse_pdf(data, mois_input, titre="BILAN FINANCIER MENSUEL")
            # Correctif : Utilisation du chemin absolu
            full_path = os.path.abspath(path)
            if os.path.exists(full_path):
                os.startfile(full_path)
            else:
                messagebox.showerror("Erreur", "Le fichier n'a pas pu être créé.")

    def sauvegarder(self):
        l, m, t = self.ent_lib.get(), self.ent_mt.get(), self.type_var.get()
        if l and m:
            try:
                self.db.query("INSERT INTO finances (libelle, montant, type) VALUES (?,?,?)", (l, float(m), t))
                self.ent_lib.delete(0, 'end')
                self.ent_mt.delete(0, 'end')
                self.refresh()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        t_in, t_out = 0, 0
        for r in self.db.query("SELECT * FROM finances ORDER BY date DESC").fetchall():
            self.tree.insert("", "end", values=(r['id'], r['date'], r['libelle'], f"{r['montant']:,.0f} FCFA", r['type']))
            if r['type'] == "ENTRÉE": t_in += r['montant']
            else: t_out += r['montant']
        self.card_in.configure(text=f"{t_in:,.0f} FCFA")
        self.card_out.configure(text=f"{t_out:,.0f} FCFA")
        self.card_solde.configure(text=f"{(t_in - t_out):,.0f} FCFA")