import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import cv2
from PIL import Image, ImageTk
from database.db_manager import Database
from config.settings import *
import os
from datetime import datetime

class PersonnelScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = Database()
        self.selected_photo_path = None
        self.selected_emp_id = None
        
        if not os.path.exists("assets/photos"):
            os.makedirs("assets/photos")
            
        self.setup_ui()

    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(header, text="Répertoire du Personnel", font=("Segoe UI", 24, "bold")).pack(side="left")
        
        self.statut_filter = ctk.CTkSegmentedButton(header, values=["Actif", "Inactif", "Tous"], command=self.load_data)
        self.statut_filter.set("Actif")
        self.statut_filter.pack(side="right", padx=10)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20)

        # --- FORMULAIRE (Scrollable pour accommoder les nouveaux champs) ---
        self.form = ctk.CTkScrollableFrame(container, fg_color=COLOR_CARD_BG, width=320)
        self.form.pack(side="left", fill="y", padx=10, pady=10)
        
        # Zone Aperçu Photo
        self.photo_container = ctk.CTkFrame(self.form, fg_color="transparent", width=120, height=120)
        self.photo_container.pack(pady=15)
        self.photo_container.pack_propagate(False)
        
        self.photo_label = ctk.CTkLabel(self.photo_container, text="AUCUNE PHOTO", fg_color="#333", corner_radius=10)
        self.photo_label.pack(fill="both", expand=True)

        btn_box = ctk.CTkFrame(self.form, fg_color="transparent")
        btn_box.pack(fill="x", padx=20)
        ctk.CTkButton(btn_box, text="📁", width=40, command=self.choose_photo_file).pack(side="left", padx=5)
        ctk.CTkButton(btn_box, text="📷 Caméra", command=self.open_camera).pack(side="left", expand=True, fill="x")

        # Champs de saisie principaux
        self.ent_mat = ctk.CTkEntry(self.form, placeholder_text="Matricule")
        self.ent_mat.pack(pady=5, padx=20, fill="x")
        self.ent_nom = ctk.CTkEntry(self.form, placeholder_text="Nom Complet")
        self.ent_nom.pack(pady=5, padx=20, fill="x")
        self.ent_sal = ctk.CTkEntry(self.form, placeholder_text="Salaire de base")
        self.ent_sal.pack(pady=5, padx=20, fill="x")
        self.ent_tel = ctk.CTkEntry(self.form, placeholder_text="Téléphone Employé")
        self.ent_tel.pack(pady=5, padx=20, fill="x")
        
        self.combo_contrat = ctk.CTkComboBox(self.form, values=["CDI", "CDD", "Journalier", "Stage"])
        self.combo_contrat.pack(pady=5, padx=20, fill="x")

        # Section Urgence
        ctk.CTkLabel(self.form, text="Contact d'Urgence", font=("Segoe UI", 12, "bold"), text_color=COLOR_ACCENT).pack(pady=(10,0))
        self.ent_urg_nom = ctk.CTkEntry(self.form, placeholder_text="Nom du contact")
        self.ent_urg_nom.pack(pady=5, padx=20, fill="x")
        self.ent_urg_tel = ctk.CTkEntry(self.form, placeholder_text="Téléphone urgence")
        self.ent_urg_tel.pack(pady=5, padx=20, fill="x")

        # Boutons d'Action
        self.btn_main = ctk.CTkButton(self.form, text="AJOUTER", fg_color=COLOR_ACCENT, command=self.save_emp)
        self.btn_main.pack(pady=(20, 5), padx=20, fill="x")
        
        self.btn_delete = ctk.CTkButton(self.form, text="SUPPRIMER", fg_color="#ef4444", command=self.delete_emp)
        # Caché par défaut

        ctk.CTkButton(self.form, text="Réinitialiser", fg_color="transparent", border_width=1, command=self.clear_form).pack(pady=5, padx=20, fill="x")

        # --- TABLEAU (DROITE) ---
        self.tree_frame = ctk.CTkFrame(container, fg_color=COLOR_CARD_BG)
        self.tree_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(self.tree_frame, columns=("id", "mat", "nom", "tel", "statut"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("mat", text="MATRICULE")
        self.tree.heading("nom", text="NOM")
        self.tree.heading("tel", text="TÉLÉPHONE")
        self.tree.heading("statut", text="STATUT")
        
        self.tree.column("id", width=0, stretch=False)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        self.load_data()

    # --- GESTION MULTIMÉDIA ---
    def update_photo_preview(self, path):
        for widget in self.photo_container.winfo_children():
            widget.destroy()

        if not path or not os.path.exists(path):
            self.photo_label = ctk.CTkLabel(self.photo_container, text="AUCUNE PHOTO", fg_color="#333", corner_radius=10)
            self.photo_label.pack(fill="both", expand=True)
            return

        try:
            img_pil = Image.open(path).resize((120, 120))
            ctk_img = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(120, 120))
            self.photo_label = ctk.CTkLabel(self.photo_container, image=ctk_img, text="")
            self.photo_label.image = ctk_img
            self.photo_label.pack(fill="both", expand=True)
        except:
            self.photo_label = ctk.CTkLabel(self.photo_container, text="ERREUR", fg_color="#522")
            self.photo_label.pack(fill="both", expand=True)

    def open_camera(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            messagebox.showerror("Erreur", "Caméra non détectée.")
            return
        cam_window = ctk.CTkToplevel(self)
        cam_window.title("Capture Photo")
        cam_window.attributes('-topmost', True)
        v_label = ctk.CTkLabel(cam_window, text="")
        v_label.pack(pady=10, padx=10)

        def update_frame():
            if not cam_window.winfo_exists():
                cap.release(); return
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)).resize((350, 260))
                imgtk = ImageTk.PhotoImage(image=img)
                v_label.configure(image=imgtk)
                v_label._img_ref = imgtk
            v_label.after(20, update_frame)

        def take_snapshot():
            ret, frame = cap.read()
            if ret:
                path = f"assets/photos/cap_{datetime.now().strftime('%H%M%S')}.jpg"
                cv2.imwrite(path, frame)
                self.selected_photo_path = path
                self.update_photo_preview(path)
                cap.release(); cam_window.destroy()

        ctk.CTkButton(cam_window, text="CAPTURER", command=take_snapshot).pack(pady=10)
        update_frame()

    def choose_photo_file(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if path:
            self.selected_photo_path = path
            self.update_photo_preview(path)

    # --- ACTIONS CRUD ---
    def save_emp(self):
        data = (
            self.ent_mat.get(), self.ent_nom.get(), self.ent_sal.get(), 
            self.ent_tel.get(), self.combo_contrat.get(), 
            self.ent_urg_nom.get(), self.ent_urg_tel.get(), 
            self.selected_photo_path
        )
        
        if not data[0] or not data[1]:
            messagebox.showwarning("Erreur", "Matricule et Nom requis.")
            return

        if self.selected_emp_id:
            query = """UPDATE personnel SET matricule=?, nom=?, salaire_base=?, telephone=?, 
                       type_contrat=?, urgence_nom=?, urgence_tel=?, photo_path=? WHERE id=?"""
            self.db.query(query, (*data, self.selected_emp_id))
        else:
            query = """INSERT INTO personnel (matricule, nom, salaire_base, telephone, 
                       type_contrat, urgence_nom, urgence_tel, photo_path, statut) 
                       VALUES (?,?,?,?,?,?,?,?,'Actif')"""
            self.db.query(query, data)
        
        self.clear_form()
        self.load_data()

    def delete_emp(self):
        if self.selected_emp_id and messagebox.askyesno("Supprimer", "Confirmer la suppression ?"):
            self.db.query("DELETE FROM personnel WHERE id=?", (self.selected_emp_id,))
            self.clear_form()
            self.load_data()

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        emp_id = self.tree.item(selected[0])['values'][0]
        res = self.db.query("SELECT * FROM personnel WHERE id=?", (emp_id,)).fetchone()
        if res:
            self.selected_emp_id = res['id']
            self.ent_mat.delete(0, 'end'); self.ent_mat.insert(0, str(res['matricule']))
            self.ent_nom.delete(0, 'end'); self.ent_nom.insert(0, str(res['nom']))
            self.ent_sal.delete(0, 'end'); self.ent_sal.insert(0, str(res['salaire_base']))
            self.ent_tel.delete(0, 'end'); self.ent_tel.insert(0, str(res['telephone'] or ""))
            self.ent_urg_nom.delete(0, 'end'); self.ent_urg_nom.insert(0, str(res['urgence_nom'] or ""))
            self.ent_urg_tel.delete(0, 'end'); self.ent_urg_tel.insert(0, str(res['urgence_tel'] or ""))
            self.combo_contrat.set(res['type_contrat'])
            self.selected_photo_path = res['photo_path']
            self.update_photo_preview(res['photo_path'])
            self.btn_main.configure(text="MODIFIER")
            self.btn_delete.pack(pady=5, padx=20, fill="x")

    def clear_form(self):
        self.selected_emp_id = None
        self.selected_photo_path = None
        for entry in [self.ent_mat, self.ent_nom, self.ent_sal, self.ent_tel, self.ent_urg_nom, self.ent_urg_tel]:
            entry.delete(0, 'end')
        self.update_photo_preview(None)
        self.btn_main.configure(text="AJOUTER")
        self.btn_delete.pack_forget()

    def load_data(self, filter_val=None):
        filter_val = filter_val or self.statut_filter.get()
        for i in self.tree.get_children(): self.tree.delete(i)
        q = "SELECT * FROM personnel" + (" WHERE statut = ?" if filter_val != "Tous" else "")
        p = (filter_val,) if filter_val != "Tous" else ()
        for r in self.db.query(q, p).fetchall():
            self.tree.insert("", "end", values=(r['id'], r['matricule'], r['nom'], r['telephone'], r['statut']))