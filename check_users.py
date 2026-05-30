import json
import os

DATA_FOLDER = 'data'
USERS_FILE = os.path.join(DATA_FOLDER, 'users.json')

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)

    print("Существующие пользователи:")
    print("-" * 40)
    for username, data in users.items():
        print(f"Логин: {username}")
        print(f"  Пароль: {data.get('password')}")
        print(f"  Роль: {data.get('role')}")
        print(f"  Имя: {data.get('fullname')}")
        print("-" * 40)
else:
    print("Файл users.json не найден!")