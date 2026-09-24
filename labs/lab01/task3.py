import hashlib
import os
import sys
import csv
import json
from datetime import datetime

# Створюємо власний клас помилки (як вимагає методичка)
class ValidationError(Exception):
    pass

# Підключаємо модуль з твоїми даними
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared.student import VARIANT_NUMBER

# Сіль для 6 варіанту (5 символів, доповнено нулями зліва)
PERSONAL_SALT = f"{VARIANT_NUMBER:05d}" # Вийде "00006"
MIN_LENGTH = 9 # З таблиці для 6 варіанту

# 1. Функція хешування
def generate_hash(password: str, salt: str = "00000") -> str:
    # Перевірка на порожні значення
    if password == "" or password is None or salt == "" or salt is None:
        raise ValueError("Пароль або сіль не можуть бути порожніми.")
    
    # Перевірка на мінімальну довжину для варіанту 6
    if len(password) < MIN_LENGTH:
        raise ValidationError("Пароль занадто короткий для 6 варіанту.")
    
    # Використовуємо blake2s згідно з таблицею
    data_to_hash = (password + salt).encode('utf-8')
    return hashlib.blake2s(data_to_hash).hexdigest()

# 2. Кортеж користувачів для реєстрації
# Я спеціально додав користувача "user2" з коротким паролем і "bot" без пароля,
# щоб показати викладачу, як програма відловлює помилки
users_to_register = (
    ("admin", "SuperSecretPassword1"),
    ("user1", "MyPassword123"),
    ("user2", "Short1"), # Викличе ValidationError (< 9 символів)
    ("guest", "GuestPass2026"),
    ("manager", "ManagerSecure99"),
    ("test_user", "TestTesting123"),
    ("student", "StudentPass_6"),
    ("hacker", "HackThePlanet1"),
    ("ceo", "BigBossPassword"),
    ("bot", "") # Викличе ValueError
)

# 3. Реєстрація користувачів
def create_user(username, password):
    hash_value = generate_hash(password, PERSONAL_SALT)
    return (username, hash_value)

def create_users(users_list):
    # Автоматично створюємо папку data
    os.makedirs("labs/lab01/data", exist_ok=True)
    path = "labs/lab01/data/users.csv"
    
    try:
        with open(path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password_hash"])
            
            for user in users_list:
                username = user[0]
                password = user[1]
                
                try:
                    user_data = create_user(username, password)
                    writer.writerow(user_data)
                except ValueError as e:
                    print(f"Помилка ValueError для {username}: {e}")
                except ValidationError as e:
                    print(f"Помилка ValidationError для {username}: {e}")
                    
    except PermissionError:
        print("Немає прав на запис файлу CSV.")
    except IOError:
        print("Помилка вводу/виводу при роботі з CSV.")

# 4. Читання бази даних
def read_db():
    users_db = []
    path = "labs/lab01/data/users.csv"
    
    try:
        with open(path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader) # Пропускаємо перший рядок (заголовки)
            
            for row in reader:
                # Зберігаємо як словник для зручності
                user_dict = {"username": row[0], "password_hash": row[1]}
                users_db.append(user_dict)
                
        print("\n--- Вміст бази даних ---")
        for u in users_db:
            print(f"Користувач: {u['username']}, Хеш: {u['password_hash'][:15]}...")
            
    except FileNotFoundError:
        print("Файл бази даних не знайдено.")
    except PermissionError:
        print("Немає прав на читання файлу CSV.")
    except IOError:
        print("Помилка читання файлу бази даних.")
        
    return users_db

# 6. Декоратор логування
def log_event(func):
    def wrapper(*args, **kwargs):
        # Виконуємо саму функцію (login)
        result = func(*args, **kwargs)
        
        # Дістаємо логін із першого аргументу
        if len(args) > 0:
            username = args[0]
        else:
            username = "Невідомо"
            
        if result == True:
            status = "success"
        else:
            status = "failure"
            
        log_entry = {
            "event": "login",
            "user": username,
            "result": status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "args": list(args),
            "kwargs": kwargs
        }
        
        os.makedirs("labs/lab01/data", exist_ok=True)
        try:
            with open("labs/lab01/data/log.json", mode="a", encoding="utf-8") as file:
                file.write(json.dumps(log_entry) + "\n")
        except (PermissionError, IOError) as e:
            print(f"Помилка запису логу: {e}")
            
        return result
    return wrapper

# 5. Автентифікація
@log_event
def login(username: str, password: str) -> bool:
    if username == "" or password == "":
        raise ValueError("Логін або пароль не можуть бути порожніми.")
        
    try:
        expected_hash = generate_hash(password, PERSONAL_SALT)
        users_db = read_db() # Читаємо базу
        
        # Шукаємо користувача і порівнюємо хеш
        for user in users_db:
            if user["username"] == username:
                if user["password_hash"] == expected_hash:
                    return True
        return False
        
    except (ValueError, ValidationError):
        return False

# 7. Головна функція для запуску
def task3():
    print("--- Реєстрація користувачів (генерація CSV) ---")
    create_users(users_to_register)
    
    print("\n--- Тестування входу (генерація JSON логів) ---")
    try:
        # Тест 1: Правильний пароль
        res1 = login("admin", "SuperSecretPassword1")
        print(f"Вхід admin (правильний пароль): {res1}")
        
        # Тест 2: Неправильний пароль
        res2 = login("user1", "WrongPassword")
        print(f"Вхід user1 (неправильний пароль): {res2}")
        
        # Тест 3: Виклик помилки ValueError (порожній пароль)
        login("guest", "")
    except ValueError as e:
        print(f"Відловлено помилку при вході: {e}")

if __name__ == "__main__":
    task3()