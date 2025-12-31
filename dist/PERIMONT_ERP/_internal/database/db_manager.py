import sqlite3
import os
from config.settings import DB_PATH

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cls._instance.conn.row_factory = sqlite3.Row
            cls._instance.cursor = cls._instance.conn.cursor()
            cls._instance.create_tables()
        return cls._instance

    def create_tables(self):
        """Initialisation des tables et déclenchement des mises à jour."""
        queries = [
            "CREATE TABLE IF NOT EXISTS utilisateurs (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)",
            "CREATE TABLE IF NOT EXISTS personnel (id INTEGER PRIMARY KEY AUTOINCREMENT, matricule TEXT UNIQUE, nom TEXT, prenom TEXT, fonction TEXT, salaire_base REAL, statut TEXT DEFAULT 'Actif', photo_path TEXT, type_contrat TEXT DEFAULT 'CDI', date_embauche DATE DEFAULT CURRENT_DATE, telephone TEXT, urgence_nom TEXT, urgence_tel TEXT)",
            "CREATE TABLE IF NOT EXISTS details_paie (id INTEGER PRIMARY KEY AUTOINCREMENT, id_personnel INTEGER, type_mouvement TEXT, montant REAL, motif TEXT, date_mouvement DATE DEFAULT CURRENT_DATE, mois_concerne TEXT, FOREIGN KEY (id_personnel) REFERENCES personnel (id))",
            "CREATE TABLE IF NOT EXISTS camions (id INTEGER PRIMARY KEY AUTOINCREMENT, immatriculation TEXT UNIQUE, modele TEXT, capacite REAL)",
            "CREATE TABLE IF NOT EXISTS engins (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, type TEXT, immatriculation TEXT UNIQUE, heures_moteur REAL DEFAULT 0, tarif_heure REAL, statut TEXT DEFAULT 'Disponible')",
            "CREATE TABLE IF NOT EXISTS locations (id INTEGER PRIMARY KEY AUTOINCREMENT, client_nom TEXT, materiel_id INTEGER, type_materiel TEXT, date_debut DATE, duree_jours INTEGER, montant_total REAL, statut TEXT DEFAULT 'En cours')",
            "CREATE TABLE IF NOT EXISTS trajets (id INTEGER PRIMARY KEY AUTOINCREMENT, camion_id INTEGER, destination TEXT, consommation_carburant REAL, date_trajet DATE DEFAULT CURRENT_DATE, FOREIGN KEY (camion_id) REFERENCES camions (id))",
            "CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY AUTOINCREMENT, nom_article TEXT UNIQUE, quantite REAL DEFAULT 0, seuil_alerte REAL DEFAULT 10, unite TEXT DEFAULT 'Unité')",
            "CREATE TABLE IF NOT EXISTS finances (id INTEGER PRIMARY KEY AUTOINCREMENT, libelle TEXT, montant REAL, type TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, titre TEXT, description TEXT, date_event DATE, categorie TEXT, priorite TEXT, statut TEXT DEFAULT 'À faire')"
        ]
        for q in queries:
            self.cursor.execute(q)
        
        self.apply_migrations()
        self.conn.commit()

    def apply_migrations(self):
        """Vérifie et injecte les colonnes manquantes sans exception bloquante."""
        tables_to_check = {
            "agenda": [
                ("date_event", "DATE"), 
                ("categorie", "TEXT"), 
                ("priorite", "TEXT DEFAULT 'Normale'"), 
                ("statut", "TEXT DEFAULT 'À faire'")
            ],
            "trajets": [
                ("destination", "TEXT"), 
                ("consommation_carburant", "REAL")
            ]
        }

        for table, columns in tables_to_check.items():
            try:
                self.cursor.execute(f"PRAGMA table_info({table})")
                existing_cols = [info[1] for info in self.cursor.fetchall()]
                for col_name, col_type in columns:
                    if col_name not in existing_cols:
                        print(f"🛠️ Migration : Ajout de {col_name} dans {table}")
                        self.cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"⚠️ Erreur mineure migration {table}: {e}")

    def query(self, sql, params=()):
        """Exécution sécurisée. Si une erreur survient, on tente de la logger précisément."""
        try:
            res = self.cursor.execute(sql, params)
            self.conn.commit()
            return res
        except sqlite3.Error as e:
            print(f"❌ ERREUR SQL CRITIQUE : {e}\nRequête : {sql}")
            # On relance l'erreur pour que l'UI sache que ça n'a pas marché 
            # (au lieu de renvoyer du vide qui fait croire que tout va bien)
            raise e