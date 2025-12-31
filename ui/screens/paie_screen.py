import customtkinter as ctk
from tkinter import ttk, messagebox
import os
from database.db_manager import Database
from config.settings import *
from datetime import datetime

class PaieScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = Database()
        self.selected_emp = None
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        left_panel = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        ctk.CTkLabel(left_panel, text="Personnel Actif", font=("Segoe UI", 16, "bold")).pack(pady=15)
        
        self.tree = ttk.Treeview(left_panel, columns=("id", "nom", "contrat"), show="headings")
        self.tree.heading("nom", text="NOM"); self.tree.heading("contrat", text="CONTRAT")
        self.tree.column("id", width=0, stretch=False)
        self.tree.pack(fill="both", expand=True, padx=15, pady=15)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_panel = ctk.CTkScrollableFrame(self, fg_color=COLOR_CARD_BG)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)

        self.liste_mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                              "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        self.combo_mois = ctk.CTkComboBox(right_panel, values=self.liste_mois_fr, width=200)
        self.combo_mois.set(self.liste_mois_fr[datetime.now().month - 1])
        self.combo_mois.pack(pady=10)

        self.ent_jours = ctk.CTkEntry(right_panel, placeholder_text="Jours (Journaliers)", width=300)
        self.ent_jours.pack(pady=5); self.ent_jours.insert(0, "0")

        self.type_mvt = ctk.CTkSegmentedButton(right_panel, values=["AVANCE", "PRIME", "RETENUE"], width=300)
        self.type_mvt.set("AVANCE"); self.type_mvt.pack(pady=10)
        
        self.ent_montant = ctk.CTkEntry(right_panel, placeholder_text="Montant (FCFA)", width=300)
        self.ent_montant.pack(pady=5)
        self.ent_motif = ctk.CTkEntry(right_panel, placeholder_text="Motif", width=300)
        self.ent_motif.pack(pady=5)
        
        ctk.CTkButton(right_panel, text="ENREGISTRER", command=self.save_mouvement, fg_color=COLOR_ACCENT).pack(pady=20)

        self.btn_pdf = ctk.CTkButton(right_panel, text="📄 BULLETIN PDF", command=self.export_pdf, state="disabled", fg_color="#10B981")
        self.btn_pdf.pack(pady=5)
        self.btn_recap_pdf = ctk.CTkButton(right_panel, text="📜 RÉCAPITULATIF PDF", command=self.export_recap_pdf, fg_color="#F59E0B")
        self.btn_recap_pdf.pack(pady=5)

        self.load_data()

    def get_mois_en(self):
        m = {"Janvier":"January","Février":"February","Mars":"March","Avril":"April","Mai":"May","Juin":"June",
             "Juillet":"July","Août":"August","Septembre":"September","Octobre":"October","Novembre":"November","Décembre":"December"}
        return m.get(self.combo_mois.get(), self.combo_mois.get())

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.db.query("SELECT id, nom, type_contrat FROM personnel WHERE statut='Actif'").fetchall():
            self.tree.insert("", "end", values=(r['id'], r['nom'], r['type_contrat']))

    def on_select(self, e):
        sel = self.tree.selection()
        if sel:
            id_emp = self.tree.item(sel[0])['values'][0]
            self.selected_emp = self.db.query("SELECT * FROM personnel WHERE id=?", (id_emp,)).fetchone()
            self.btn_pdf.configure(state="normal")
            d = self.get_details_mois(id_emp)
            self.ent_jours.delete(0, 'end'); self.ent_jours.insert(0, str(int(d['jours_travailles'])))

    def save_mouvement(self):
        if not self.selected_emp: return
        mois_annee = f"{self.get_mois_en()} {datetime.now().year}"
        self.db.query("DELETE FROM details_paie WHERE id_personnel=? AND mois_concerne=? AND type_mouvement='PRESENCE'", (self.selected_emp['id'], mois_annee))
        self.db.query("INSERT INTO details_paie (id_personnel, type_mouvement, montant, motif, mois_concerne) VALUES (?,?,?,?,?)",
                      (self.selected_emp['id'], 'PRESENCE', float(self.ent_jours.get() or 0), 'Presence', mois_annee))
        if self.ent_montant.get():
            self.db.query("INSERT INTO details_paie (id_personnel, type_mouvement, montant, motif, mois_concerne) VALUES (?,?,?,?,?)",
                          (self.selected_emp['id'], self.type_mvt.get(), float(self.ent_montant.get()), self.ent_motif.get(), mois_annee))
        messagebox.showinfo("Succès", "Données mises à jour")

    def get_details_mois(self, id_emp):
        mois_annee = f"{self.get_mois_en()} {datetime.now().year}"
        res = self.db.query("SELECT type_mouvement, SUM(montant) as total FROM details_paie WHERE id_personnel=? AND mois_concerne=? GROUP BY type_mouvement", (id_emp, mois_annee)).fetchall()
        d = {'avances':0, 'primes':0, 'retenues':0, 'jours_travailles':0}
        for r in res:
            if r['type_mouvement'] == 'AVANCE': d['avances'] = r['total']
            elif r['type_mouvement'] == 'PRIME': d['primes'] = r['total']
            elif r['type_mouvement'] == 'RETENUE': d['retenues'] = r['total']
            elif r['type_mouvement'] == 'PRESENCE': d['jours_travailles'] = r['total']
        return d

    def export_pdf(self):
        try:
            details = self.get_details_mois(self.selected_emp['id'])
            sb = self.selected_emp['salaire_base'] or 0
            if self.selected_emp['type_contrat'] == "Journalier":
                sb = sb * details['jours_travailles']
            details['salaire_base_calcule'] = sb
            from utils.pdf_generator import generer_bulletin
            path = generer_bulletin(self.selected_emp, self.get_mois_en(), datetime.now().year, details)
            if os.path.exists(path): os.startfile(os.path.abspath(path))
        except PermissionError:
            messagebox.showerror("Erreur", "Fermez le bulletin PDF s'il est déjà ouvert.")

    def export_recap_pdf(self):
        try:
            emps = self.db.query("SELECT * FROM personnel WHERE statut='Actif'").fetchall()
            data_list, total_g = [], 0
            for e in emps:
                d = self.get_details_mois(e['id'])
                sb = (e['salaire_base'] or 0) * (d['jours_travailles'] if e['type_contrat']=="Journalier" else 1)
                ret_tot = d['avances'] + d['retenues']
                net = sb + d['primes'] - ret_tot
                data_list.append({
                    'Matricule': e['matricule'], 'Nom': e['nom'], 
                    'S. Base': sb, 'Primes': d['primes'], 
                    'Retenues': ret_tot, 'NET': net
                })
                total_g += net
            from utils.pdf_generator import generer_recap_mensuel_pdf
            path = generer_recap_mensuel_pdf(data_list, self.get_mois_en(), datetime.now().year, total_g)
            if os.path.exists(path): os.startfile(os.path.abspath(path))
        except PermissionError:
            messagebox.showerror("Erreur", "Fermez le récapitulatif PDF s'il est déjà ouvert.")