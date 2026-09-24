import hashlib
import os
import sys
import csv
import json
from datetime import datetime

class ValidationError(Exception):
    pass

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared.student import VARIANT_NUMBER

PERSONAL_SALT = f"{VARIANT_NUMBER:05d}"
MIN_LENGTH = 9 

def generate_hash(password: str, salt: str = "00000") -> str:
    if password == "" or password is None or salt == "" or salt is None:
        raise ValueError("Пароль або сіль не можуть бути порожніми.")
    
    if len(password) < MIN_LENGTH:
        raise ValidationError("Пароль занадто короткий для 6 варіанту.")
    
    data_to_hash = (password + salt).encode('utf-8')
    return hashlib.blake2s(data_to_hash).hexdigest()

users_to_register = (
    ("admin", "SuperSecretPassword1"),
    ("user1", "MyPassword123"),
    ("user2", "Short1"), 
    ("guest", "GuestPass2026"),
    ("manager", "ManagerSecure99"),
    ("test_user", "TestTesting123"),
    ("student", "StudentPass_6"),
    ("hacker", "HackThePlanet1"),
    ("ceo", "BigBossPassword"),
)

def create_user(username, password):
    hash_value = generate_hash(password, PERSONAL_SALT)
    return (username, hash_value)

def create_users(users_list):
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

def read_db():
    users_db = []
    path = "labs/lab01/data/users.csv"
    
    try:
        with open(path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader) 
            
            for row in reader:
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

def log_event(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
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

@log_event
def login(username: str, password: str) -> bool:
    if username == "" or password == "":
        raise ValueError("Логін або пароль не можуть бути порожніми.")
        
    try:
        expected_hash = generate_hash(password, PERSONAL_SALT)
        users_db = read_db() 
        
        for user in users_db:
            if user["username"] == username:
                if user["password_hash"] == expected_hash:
                    return True
        return False
        
    except (ValueError, ValidationError):
        return False

def task3():
    print("--- Реєстрація користувачів (генерація CSV) ---")
    create_users(users_to_register)
    
    print("\n--- Тестування входу (генерація JSON логів) ---")
    try:
        res1 = login("admin", "SuperSecretPassword1")
        print(f"Вхід admin (правильний пароль): {res1}")
        
        res2 = login("user1", "WrongPassword")
        print(f"Вхід user1 (неправильний пароль): {res2}")
        
        login("guest", "")
    except ValueError as e:
        print(f"Відловлено помилку при вході: {e}")

if __name__ == "__main__":
    task3()