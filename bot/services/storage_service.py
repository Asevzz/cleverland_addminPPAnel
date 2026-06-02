import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from shared.firebase_config import get_bucket
import uuid

bucket = get_bucket()

class StorageService:

    @staticmethod
    def upload_image(file_data, file_name=None):
        """Загрузить изображение в Firebase Storage"""
        if not file_name:
            file_name = f"questions/{uuid.uuid4()}.jpg"

        blob = bucket.blob(file_name)
        blob.upload_from_string(file_data, content_type='image/jpeg')
        blob.make_public()

        return blob.public_url

    @staticmethod
    def delete_image(file_name):
        """Удалить изображение из Firebase Storage"""
        blob = bucket.blob(file_name)
        blob.delete()
        return True
