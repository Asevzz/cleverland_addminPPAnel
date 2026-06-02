import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

import os
import firebase_admin
from firebase_admin import credentials, firestore, storage

def initialize_firebase():
    """Инициализация Firebase"""
    if not firebase_admin._apps:
        cred_path = os.path.join(os.path.dirname(__file__), '..', 'serviceAccountKey.json')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'cleverlandctbot.appspot.com'  # ← ваш bucket
        })

def get_db():
    """Получить Firestore клиент"""
    initialize_firebase()
    return firestore.client()

def get_storage():
    """Получить Storage клиент"""
    initialize_firebase()
    return storage