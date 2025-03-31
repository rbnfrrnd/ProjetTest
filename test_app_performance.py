import unittest
import time
import io
from app import app

class PerformanceTestCase(unittest.TestCase):

    def setUp(self):
        """Configuration pour chaque test"""
        self.client = app.test_client()

        # Simuler un utilisateur connecté en tant qu'administrateur dans la session
        with self.client.session_transaction() as session:
            # Simuler un utilisateur avec des droits administratifs
            session['current_user'] = 'admin'  # Nom de l'utilisateur
            session['user_role'] = 'admin'  # Rôle de l'utilisateur

    def test_upload_performance(self):
        """Tester le temps de réponse de l'upload d'une image"""

        # Simuler une image en utilisant un flux de données
        fake_image = io.BytesIO(b"fake image data")  # 'b' préfixe pour les bytes

        # Définir le nom de fichier de l'image
        fake_image.filename = 'test_image.jpg'

        # Démarrer le chronomètre
        start_time = time.time()

        # Effectuer la requête POST pour uploader l'image
        response = self.client.post(
            '/upload_image',
            data={'file': (fake_image, 'test_image.jpg')},
            content_type='multipart/form-data'
        )

        # Simuler un délai (2 secondes) avec sleep pour la simulation de performance
        time.sleep(2)

        # Si le code est 302, cela signifie qu'il y a eu une redirection
        if response.status_code == 302:
            # Suivre la redirection
            response = self.client.get(response.location)

        # Calculer le temps de réponse
        response_time = time.time() - start_time

        # Vérifier que le code de réponse est 200 OK
        self.assertEqual(response.status_code, 200, f"Code de réponse attendu: 200, mais obtenu: {response.status_code}")

        # Vérifier que le temps de réponse est raisonnable (par exemple, moins de 5 secondes)
        self.assertLess(response_time, 5, f"Temps de réponse trop long: {response_time} secondes")

if __name__ == '__main__':
    unittest.main()
