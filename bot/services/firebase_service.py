import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from shared.firebase_config import get_db
from bot.config import SUBJECTS
import random
import string

db = get_db()

class FirebaseService:

    @staticmethod
    def get_student(tg_id):
        """Получить данные ученика по Telegram ID"""
        doc = db.collection('students').document(str(tg_id)).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def create_student(tg_id, username, first_name, last_name=""):
        """Создать запись ученика"""
        db.collection('students').document(str(tg_id)).set({
            'tg_id': tg_id,
            'username': username or "",
            'first_name': first_name or "",
            'last_name': last_name or "",
            'subjects': {},
            'registered_at': firestore.SERVER_TIMESTAMP
        })

    @staticmethod
    def get_key(key_code):
        """Получить ключ активации"""
        doc = db.collection('activation_keys').document(key_code.upper()).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def activate_key(key_code, tg_id):
        """Активировать ключ для ученика"""
        key_ref = db.collection('activation_keys').document(key_code.upper())
        key_doc = key_ref.get()

        if not key_doc.exists:
            return None, "Ключ не найден"

        key_data = key_doc.to_dict()

        if key_data.get('is_used'):
            return None, "Ключ уже использован"

        # Активируем ключ
        key_ref.update({
            'student_tg_id': tg_id,
            'is_used': True,
            'activated_at': firestore.SERVER_TIMESTAMP
        })

        # Добавляем предмет ученику
        student_ref = db.collection('students').document(str(tg_id))
        student_doc = student_ref.get()

        if not student_doc.exists:
            return None, "Ученик не найден"

        student_data = student_doc.to_dict()
        subjects = student_data.get('subjects', {})
        subjects[key_data['subject_id']] = key_code.upper()

        student_ref.update({'subjects': subjects})

        return key_data['subject_id'], None

    @staticmethod
    def get_tests_by_subject_and_part(subject_id, part=None, teacher_id=None):
        """Получить тесты по предмету и части"""
        query = db.collection('tests').where('subject_id', '==', subject_id).where('is_active', '==', True)

        if part:
            query = query.where('part', '==', part)

        if teacher_id:
            query = query.where('teacher_id', '==', teacher_id)

        docs = query.stream()
        tests = []
        for doc in docs:
            test = doc.to_dict()
            test['id'] = doc.id
            tests.append(test)
        return tests

    @staticmethod
    def get_test(test_id):
        """Получить тест по ID"""
        doc = db.collection('tests').document(test_id).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def save_answer(student_tg_id, test_id, question_index, given_answer, is_correct, part):
        """Сохранить ответ ученика"""
        db.collection('answers').add({
            'student_tg_id': student_tg_id,
            'test_id': test_id,
            'question_index': question_index,
            'given_answer': given_answer,
            'is_correct': is_correct,
            'part': part,
            'answered_at': firestore.SERVER_TIMESTAMP
        })

    @staticmethod
    def clear_answers(student_tg_id, test_id):
        """Удалить старые ответы ученика по тесту перед новым прохождением"""
        docs = db.collection('answers').where('student_tg_id', '==', student_tg_id).where('test_id', '==', test_id).stream()
        for doc in docs:
            doc.reference.delete()

    @staticmethod
    def get_teacher(login):
        """Получить преподавателя по логину"""
        docs = db.collection('teachers').where('login', '==', login).limit(1).stream()
        for doc in docs:
            return doc.to_dict()
        return None

    @staticmethod
    def create_key(subject_id, created_by="admin"):
        """Создать новый ключ активации"""
        code = '-'.join([''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(4)])

        db.collection('activation_keys').document(code).set({
            'code': code,
            'subject_id': subject_id,
            'student_tg_id': None,
            'is_used': False,
            'created_by': created_by,
            'created_at': firestore.SERVER_TIMESTAMP
        })

        return code

    @staticmethod
    def unbind_key(key_code):
        """Отвязать ключ от ученика"""
        key_ref = db.collection('activation_keys').document(key_code.upper())
        key_doc = key_ref.get()

        if not key_doc.exists:
            return False

        key_data = key_doc.to_dict()
        tg_id = key_data.get('student_tg_id')
        subject_id = key_data.get('subject_id')

        # Сбрасываем ключ
        key_ref.update({
            'student_tg_id': None,
            'is_used': False,
            'activated_at': None
        })

        # Удаляем предмет у ученика
        if tg_id:
            student_ref = db.collection('students').document(str(tg_id))
            student_doc = student_ref.get()
            if student_doc.exists:
                subjects = student_doc.to_dict().get('subjects', {})
                if subject_id in subjects:
                    del subjects[subject_id]
                    student_ref.update({'subjects': subjects})

        return True

    @staticmethod
    def get_all_keys():
        """Получить все ключи"""
        docs = db.collection('activation_keys').stream()
        return [doc.to_dict() for doc in docs]

    @staticmethod
    def get_student_answers(student_tg_id, test_id=None):
        """Получить ответы ученика"""
        query = db.collection('answers').where('student_tg_id', '==', student_tg_id)
        if test_id:
            query = query.where('test_id', '==', test_id)
        docs = query.stream()
        return [doc.to_dict() for doc in docs]

from google.cloud import firestore