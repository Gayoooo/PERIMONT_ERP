import customtkinter as ctk
from tkinter import ttk, messagebox
from database.db_manager import Database
from config.settings import *
from datetime import datetime
from utils.pdf_generator import generer_bon_location_pdf

class LogistiqueScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = Database()
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="Logistique & Location d'Engins", 
                     font=("Segoe UI", 24, "bold"), text_color=COLOR_ACCENT).pack(pady=20, padx=30, anchor="w")

        self.tabview = ctk.CTkTabview(self, fg_color=COLOR_CARD_BG, segmented_button_selected_color=COLOR_ACCENT)
        self.tabview.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.tab_flotte = self.tabview.add("Camions")
        self.tab_engins = self.tabview.add("Parc Engins")
        self.tab_locations = self.tabview.add("Locations")
        self.tab_trajets = self.tabview.add("Suivi Trajets")

        self.setup_flotte_ui()
        self.setup_engins_ui()
        self.setup_locations_ui()
        self.setup_trajets_ui()

    def setup_flotte_ui(self):
        form = ctk.CTkFrame(self.tab_flotte, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=10)
        self.ent_immat = ctk.CTkEntry(form, placeholder_text="Immatriculation", width=180)
        self.ent_immat.grid(row=0, column=0, padx=10)
        self.ent_modele = ctk.CTkEntry(form, placeholder_text="Modèle/Marque", width=180)
        self.ent_modele.grid(row=0, column=1, padx=10)
        ctk.CTkButton(form, text="AJOUTER CAMION", fg_color=COLOR_ACCENT, command=self.ajouter_camion).grid(row=0, column=2, padx=10)
        
        self.tree_camions = self.create_styled_tree(self.tab_flotte, ("ID", "IMMATRICULATION", "MODÈLE"))
        self.tree_camions.pack(fill="both", expand=True, padx=20, pady=10)
        self.charger_camions()

    def setup_engins_ui(self):
        form = ctk.CTkFrame(self.tab_engins, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=10)
        self.ent_nom_engin = ctk.CTkEntry(form, placeholder_text="Nom (ex: Poclain 300)", width=150)
        self.ent_nom_engin.grid(row=0, column=0, padx=5)
        self.combo_type_engin = ctk.CTkComboBox(form, values=["Poclain", "Bulldozer", "Niveleuse", "Chargeuse"], width=150)
        self.combo_type_engin.grid(row=0, column=1, padx=5)
        self.ent_tarif_engin = ctk.CTkEntry(form, placeholder_text="Tarif/Jour (CFA)", width=120)
        self.ent_tarif_engin.grid(row=0, column=2, padx=5)
        ctk.CTkButton(form, text="+ ENGIN", fg_color=COLOR_ACCENT, command=self.ajouter_engin).grid(row=0, column=3, padx=5)

        self.tree_engins = self.create_styled_tree(self.tab_engins, ("ID", "NOM", "TYPE", "TARIF/J", "STATUT"))
        self.tree_engins.pack(fill="both", expand=True, padx=20, pady=10)
        self.charger_engins()

    def setup_locations_ui(self):
        form = ctk.CTkFrame(self.tab_locations, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=10)
        self.ent_client = ctk.CTkEntry(form, placeholder_text="Nom du Client", width=150)
        self.ent_client.grid(row=0, column=0, padx=5)
        self.combo_mat = ctk.CTkComboBox(form, values=["Chargement..."], width=180)
        self.combo_mat.grid(row=0, column=1, padx=5)
        self.ent_duree = ctk.CTkEntry(form, placeholder_text="Jours", width=60)
        self.ent_duree.grid(row=0, column=2, padx=5)
        ctk.CTkButton(form, text="CRÉER LOCATION & PDF", fg_color="#10B981", command=self.valider_location).grid(row=0, column=3, padx=5)

        self.tree_loc = self.create_styled_tree(self.tab_locations, ("ID", "CLIENT", "MATÉRIEL", "TOTAL", "STATUT"))
        self.tree_loc.pack(fill="both", expand=True, padx=20, pady=10)
        self.actualiser_liste_materiel()

    def setup_trajets_ui(self):
        form = ctk.CTkFrame(self.tab_trajets, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=10)
        self.combo_camion = ctk.CTkComboBox(form, values=["..."], width=150)
        self.combo_camion.grid(row=0, column=0, padx=5)
        self.ent_dest = ctk.CTkEntry(form, placeholder_text="Destination", width=150)
        self.ent_dest.grid(row=0, column=1, padx=5)
        self.ent_carb = ctk.CTkEntry(form, placeholder_text="Litres", width=80)
        self.ent_carb.grid(row=0, column=2, padx=5)
        ctk.CTkButton(form, text="OK", fg_color="#10B981", command=self.enregistrer_trajet).grid(row=0, column=3, padx=5)
        
        self.tree_trajets = self.create_styled_tree(self.tab_trajets, ("DATE", "CAMION", "DESTINATION", "LITRES"))
        self.tree_trajets.pack(fill="both", expand=True, padx=20, pady=10)
        self.charger_trajets()

    # LOGIQUE
    def ajouter_engin(self):
        nom, type_e, tarif = self.ent_nom_engin.get(), self.combo_type_engin.get(), self.ent_tarif_engin.get()
        if nom and tarif:
            self.db.query("INSERT INTO engins (nom, type, tarif_heure, statut) VALUES (?,?,?,?)", (nom, type_e, tarif, "Disponible"))
            self.charger_engins()
            self.actualiser_liste_materiel()
            messagebox.showinfo("Succès", f"{nom} ajouté au parc.")

    def valider_location(self):
        client = self.ent_client.get()
        materiel_str = self.combo_mat.get()
        duree = self.ent_duree.get()
        if not (client and duree and "ID:" in materiel_str): return

        mat_id = materiel_str.split("ID:")[1]
        tarif = self.db.query("SELECT tarif_heure FROM engins WHERE id=?", (mat_id,)).fetchone()[0]
        total = float(tarif) * int(duree)

        # 1. Enregistrer Location
        self.db.query("INSERT INTO locations (client_nom, materiel_id, duree_jours, montant_total) VALUES (?,?,?,?)",
                      (client, mat_id, duree, total))
        
        # 2. Automatisation FINANCES (Entrée de fonds)
        self.db.query("INSERT INTO finances (libelle, montant, type) VALUES (?,?,?)",
                      (f"Location {materiel_str} - Client: {client}", total, "ENTRÉE"))

        # 3. Générer PDF
        loc_data = {"client": client, "materiel": materiel_str, "duree": duree, "total": total}
        path = generer_bon_location_pdf(loc_data)
        
        messagebox.showinfo("Succès", f"Location enregistrée !\nBon PDF généré dans exports/\nRevenu ajouté aux finances.")
        os.startfile(path) if os.name == 'nt' else None

    def create_styled_tree(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
        return tree

    def charger_camions(self):
        for i in self.tree_camions.get_children(): self.tree_camions.delete(i)
        for r in self.db.query("SELECT * FROM camions").fetchall():
            self.tree_camions.insert("", "end", values=(r['id'], r['immatriculation'], r['modele']))

    def charger_engins(self):
        for i in self.tree_engins.get_children(): self.tree_engins.delete(i)
        for r in self.db.query("SELECT * FROM engins").fetchall():
            self.tree_engins.insert("", "end", values=(r['id'], r['nom'], r['type'], r['tarif_heure'], r['statut']))

    def charger_trajets(self):
        for i in self.tree_trajets.get_children(): self.tree_trajets.delete(i)
        for r in self.db.query("SELECT date_trajet, immatriculation, destination, consommation_carburant FROM trajets JOIN camions ON trajets.camion_id = camions.id ORDER BY trajets.id DESC").fetchall():
            self.tree_trajets.insert("", "end", values=(r[0], r[1], r[2], r[3]))

    def actualiser_liste_materiel(self):
        engins = [f"{r['nom']} (ID:{r['id']})" for r in self.db.query("SELECT id, nom FROM engins").fetchall()]
        self.combo_mat.configure(values=engins)

    def ajouter_camion(self):
        immat, mod = self.ent_immat.get().upper(), self.ent_modele.get()
        if immat and mod:
            self.db.query("INSERT INTO camions (immatriculation, modele) VALUES (?,?)", (immat, mod))
            self.charger_camions()

    def enregistrer_trajet(self):
        camion = self.combo_camion.get()
        dest = self.ent_dest.get()
        try:
            conso = float(self.ent_carb.get())
            date_now = datetime.now().strftime("%d/%m/%Y %H:%M")
            res = self.db.query("SELECT id FROM camions WHERE immatriculation=?", (camion,)).fetchone()
            if res:
                camion_id = res['id']
                self.db.query("INSERT INTO trajets (camion_id, destination, consommation_carburant, date_trajet) VALUES (?,?,?,?)",
                              (camion_id, dest, conso, date_now))
                self.db.query("UPDATE stock SET quantite = quantite - ? WHERE nom_article = 'GAZOLE'", (conso,))
                messagebox.showinfo("Succès", "Trajet enregistré et stock mis à jour.")
                self.charger_trajets()
        except Exception as e:
            messagebox.showerror("Erreur", f"Données invalides : {e}")
        pass