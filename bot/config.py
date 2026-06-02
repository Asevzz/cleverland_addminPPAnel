import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

import os

BOT_TOKEN = "8868209659:AAHU3Vi0AhUXFqw5fg6QpwZJAuC-5AcP2sw"

# Состояния ConversationHandler
STATE_WAITING_KEY = 1
STATE_WAITING_NAME = 2  # ← ДОБАВЛЕНО

SUBJECTS = {
    'history_belarus': {
        'name': 'История Беларуси',
        'type': 'ct',
        'parts': ['А', 'Б', 'В']
    },
    'english': {
        'name': 'Английский',
        'type': 'ce',
        'parts': ['A', 'B', 'C']
    },
    'society': {
        'name': 'Обществоведение',
        'type': 'ct',
        'parts': ['А', 'Б', 'В']
    }
}