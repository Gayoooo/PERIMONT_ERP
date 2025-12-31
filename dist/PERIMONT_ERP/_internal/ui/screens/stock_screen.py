import customtkinter as ctk
from tkinter import ttk, messagebox
from database.db_manager import Database
from config.settings import *

class StockScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = Database()
        self.setup_ui()

    def setup_ui(self):
        # Titre aligné avec ton style MainWindow
        ctk.CTkLabel(self, text="Gestion des Stocks & Carburant", 
                     font=("Segoe UI", 24, "bold"), text_color=COLOR_ACCENT).pack(pady=20, padx=30, anchor="w")

        # --- FORMULAIRE ---
        self.form = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=15)
        self.form.pack(fill="x", padx=30, pady=10)

        # Grille pour les entrées
        self.ent_article = ctk.CTkEntry(self.form, placeholder_text="Article (ex: Gazole)", width=200, height=40)
        self.ent_article.grid(row=0, column=0, padx=15, pady=20)

        self.ent_qte = ctk.CTkEntry(self.form, placeholder_text="Quantité (+ ou -)", width=150, height=40)
        self.ent_qte.grid(row=0, column=1, padx=15, pady=20)

        self.ent_seuil = ctk.CTkEntry(self.form, placeholder_text="Seuil d'alerte", width=120, height=40)
        self.ent_seuil.grid(row=0, column=2, padx=15, pady=20)
        self.ent_seuil.insert(0, "50") # Seuil par défaut pour le gazole par ex.

        ctk.CTkButton(self.form, text="MISE À JOUR", fg_color=COLOR_ACCENT, text_color=COLOR_SIDEBAR,
                      font=("Segoe UI", 12, "bold"), height=40, command=self.maj_stock).grid(row=0, column=3, padx=15, pady=20)

        # --- TABLEAU DES STOCKS ---
        self.tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tree_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Style Treeview adapté à ton thème sombre
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=COLOR_CARD_BG, foreground=COLOR_TEXT_MAIN, 
                        fieldbackground=COLOR_CARD_BG, borderwidth=0, rowheight=35)
        style.map("Treeview", background=[('selected', COLOR_ACCENT)], foreground=[('selected', COLOR_SIDEBAR)])

        self.tree = ttk.Treeview(self.tree_frame, columns=("art", "qte", "seuil", "status"), show="headings")
        self.tree.heading("art", text="ARTICLE")
        self.tree.heading("qte", text="QUANTITÉ")
        self.tree.heading("seuil", text="SEUIL ALERTE")
        self.tree.heading("status", text="ÉTAT")
        
        # Tags pour les alertes visuelles
        self.tree.tag_configure('alerte', foreground=COLOR_ERROR)
        
        self.tree.pack(fill="both", expand=True)
        self.charger_donnees()

    def maj_stock(self):
        art = self.ent_article.get().strip().upper()
        try:
            val = float(self.ent_qte.get())
            seuil = float(self.ent_seuil.get()) if self.ent_seuil.get() else 10
            
            res = self.db.query("SELECT quantite FROM stock WHERE nom_article=?", (art,)).fetchone()
            if res:
                self.db.query("UPDATE stock SET quantite = quantite + ?, seuil_alerte = ? WHERE nom_article=?", (val, seuil, art))
            else:
                self.db.query("INSERT INTO stock (nom_article, quantite, seuil_alerte) VALUES (?,?,?)", (art, val, seuil))
            
            messagebox.showinfo("Succès", f"Stock de {art} mis à jour.")
            self.ent_article.delete(0, 'end'); self.ent_qte.delete(0, 'end')
            self.charger_donnees()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez saisir des nombres valides.")

    def charger_donnees(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.db.query("SELECT * FROM stock").fetchall():
            tag = 'alerte' if r['quantite'] <= r['seuil_alerte'] else ''
            status = "⚠️ BAS" if r['quantite'] <= r['seuil_alerte'] else "OK"
            self.tree.insert("", "end", values=(r['nom_article'], f"{r['quantite']}", r['seuil_alerte'], status), tags=(tag,))