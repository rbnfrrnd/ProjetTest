import os
SECRET_KEY = os.getenv("SECRET_KEY", "a3f4c0e2b7e923f9a8d2a4e6d1c5b7f62e3a4c9b8d7e1a6f5c3d2b4a9f8e7c6d")
UPLOAD_FOLDER = "image_pool"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024