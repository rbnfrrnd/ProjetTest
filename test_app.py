import unittest
from app import app

class TestUserCRUD(unittest.TestCase):
    def setUp(self):
        """Configurer un client de test avec une session simulée"""
        app.testing = True
        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["current_user"] = "ADMIN"  # Simuler un admin connecté


        #ajout d'un utilisateur
    def test_add_user(self):
        """Tester l'ajout d'un utilisateur"""
        response = self.client.post("/add_user", data={"id": "testuser", "pw": "testpass"})
        self.assertEqual(response.status_code, 302)  # Redirection après ajout
        #suppresion d'un utilisateur
    def test_delete_user(self):
        """Tester la suppression d'un utilisateur"""
        response = self.client.get("/delete_user/testuser/")
        self.assertEqual(response.status_code, 302)  # Redirection après suppression
        #teste le login    
    def test_login(self):
        """Tester la connexion d'un utilisateur"""
        response = self.client.post("/login", data={"id": "testuser", "pw": "testpass"})
        self.assertEqual(response.status_code, 302)  # Redirection après connexion
        #test déconexions 
    def test_logout(self):
        """Tester la déconnexion"""
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)  # Redirection après déconnexion
   

