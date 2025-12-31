import sqlite3
from database.db_manager import Database

def seed_test_data():
    db = Database()
    
    # 1. Insertion de 10 Employés (Mélange CDI et Journaliers)
    employes = [
        ('MAT001', 'Jean Dupont', 450000, 'CDI', 'Actif'),
        ('MAT002', 'Marie Lourenco', 350000, 'CDI', 'Actif'),
        ('MAT003', 'Pierre Kalonji', 15000, 'Journalier', 'Actif'),
        ('MAT004', 'Alice Mvoula', 12000, 'Journalier', 'Actif'),
        ('MAT005', 'Robert Ngoma', 500000, 'CDI', 'Actif'),
        ('MAT006', 'Pauline Zola', 15000, 'Journalier', 'Actif'),
        ('MAT007', 'Victor Hugo', 250000, 'CDD', 'Actif'),
        ('MAT008', 'Sonia Mabiala', 300000, 'CDI', 'Actif'),
        ('MAT009', 'Kevin Tati', 10000, 'Journalier', 'Actif'),
        ('MAT010', 'Grace Mavoungou', 400000, 'CDI', 'Actif')
    ]
    
    for emp in employes:
        db.query("INSERT OR IGNORE INTO personnel (matricule, nom, salaire_base, type_contrat, statut) VALUES (?,?,?,?,?)", emp)

    # 2. Insertion de 4 Porte-chars (Camions)
    camions = [
        ('PN-123-AA', 'Mercedes Actros Porte-Char', 40),
        ('PN-456-BB', 'Volvo FH16 Porte-Char', 50),
        ('PN-789-CC', 'Scania R500 Porte-Char', 45),
        ('PN-000-DD', 'MAN TGX Porte-Char', 40)
    ]
    
    for cam in camions:
        db.query("INSERT OR IGNORE INTO camions (immatriculation, modele, capacite) VALUES (?,?,?)", cam)

    # 3. Insertion de 3 Poclains (Engins)
    engins = [
        ('Poclain 90B', 'Pelle Hydraulique', 'ENG-001', 15000, 'Disponible'),
        ('Poclain TY45', 'Pelle sur pneus', 'ENG-002', 12000, 'Disponible'),
        ('Poclain 60P', 'Pelle de terrassement', 'ENG-003', 18000, 'Disponible')
    ]
    
    for eng in engins:
        db.query("INSERT OR IGNORE INTO engins (nom, type, immatriculation, tarif_heure, statut) VALUES (?,?,?,?,?)", eng)

    print("✅ Test intégral : 10 Employés, 4 Porte-chars et 3 Poclains ajoutés !")

if __name__ == "__main__":
    seed_test_data()