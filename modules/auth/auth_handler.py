from database.db_manager import Database

class AuthHandler:
    def __init__(self):
        self.db = Database()
        self.current_user = None

    def login(self, username, password):
        # Pour le premier lancement, on crée un admin par défaut si la table est vide
        check_users = self.db.query("SELECT COUNT(*) as count FROM utilisateurs").fetchone()
        if check_users['count'] == 0:
            self.db.query("INSERT INTO utilisateurs (username, password, role) VALUES (?, ?, ?)", 
                         ('admin', 'admin123', 'Administrateur'))

        user = self.db.query("SELECT * FROM utilisateurs WHERE username=? AND password=?", 
                            (username, password)).fetchone()
        
        if user:
            self.current_user = {"id": user['id'], "username": user['username'], "role": user['role']}
            return True, self.current_user
        return False, None