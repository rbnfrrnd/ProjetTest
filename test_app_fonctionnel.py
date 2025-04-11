import unittest
from unittest.mock import patch
import io 
from app import app

class ImageUploadDeleteTestCase(unittest.TestCase):

    @patch('app.image_upload_record')  # Mock la fonction image_upload_record
    def test_upload_and_delete_image(self, mock_image_upload_record):
        with app.test_client() as client:
            # Simuler un utilisateur connecté dans la session
            with client.session_transaction() as session:
                session['current_user'] = 'test_user'  # Simuler un utilisateur

            # Préparer des données d'image factices pour le test
            file_data = {
                'file': (io.BytesIO(b"fake image data"), 'test_image.jpg')
            }

            # Test de l'upload de l'image
            response_upload = client.post("/upload_image", data=file_data, content_type="multipart/form-data", follow_redirects=True)

            # Vérifier que la fonction image_upload_record a été appelée
            mock_image_upload_record.assert_called_once()

            # Test de la suppression de l'image
            # Simuler un ID d'image que tu veux supprimer
            image_uid = 'fake_image_uid'
            response_delete = client.get(f"/delete_image/{image_uid}", follow_redirects=True)

if __name__ == '__main__':
    unittest.main()
