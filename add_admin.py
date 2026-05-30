import json
import os

DATA_FOLDER = 'data'
USERS_FILE = os.path.join(DATA_FOLDER, 'users.json')

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

users = load_users()

# Добавляем администратора
users['admin'] = {
    'password': 'admin123',
    'fullname': 'Администратор системы',
    'group': '',
    'subgroup': '',
    'role': 'admin'
}

save_users(users)
print("✅ Администратор добавлен!")
print("Логин: admin")
print("Пароль: admin123")