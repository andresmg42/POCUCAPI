# users/apps.py
import os
from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"  

    def ready(self):
        
        FIREBASE_KEY_PATH = os.environ.get(
            "FIREBASE_KEY_PATH", "pocuc/firebase_key.json"
        )

        try:
            
            firebase_admin.get_app()
        except ValueError:
            
            if os.path.exists(FIREBASE_KEY_PATH):
                cred = credentials.Certificate(FIREBASE_KEY_PATH)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK initialized successfully.")
            else:
                print(f"Warning: Firebase key not found at {FIREBASE_KEY_PATH}")
