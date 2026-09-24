import random
import sys
import os

# Додаємо шлях для імпорту з shared
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import VARIANT_NUMBER

# Вхідні дані для 6 варіанту
passwords = [
    "InfoS3c@2023", "simple123", "Def3ns3@Key", "public",
    "Encrypt3d#Pass", "basic123", "Secur3@Analysis", "temp123", 
    "Prot3ct@Data", "default"
]
criteria = {
    "min_length": 8, 
    "require_digits": True, 
    "require_upper": True,
    "require_special": True
}
forbidden_passwords = {"simple123", "public", "basic123", "temp123", "default", "guest"}

def analyze_passwords():
    # 1. Створюємо 3 дублікати через звичайний цикл
    for i in range(3):
        random_index = random.randint(0, len(passwords) - 1)
        random_password = passwords[random_index]
        passwords.append(random_password)
    
    # 2. Шапка таблиці
    print("Пароль                    | Статус")
    print("-----------------------------------------")
    
    # 3. Перевіряємо кожен пароль
    for pas in passwords:
        # Створюємо прості змінні-прапорці
        has_digit = False
        has_upper = False
        has_lower = False
        has_special = False
        
        # Перевіряємо кожну букву в паролі окремо
        for char in pas:
            if char.isdigit():
                has_digit = True
            elif char.isupper():
                has_upper = True
            elif char.islower():
                has_lower = True
            elif not char.isalnum():
                has_special = True
                
        # Рахуємо, скільки разів пароль зустрічається у списку
        count_pass = passwords.count(pas)
        
        # 4. Дерево умов (розписане максимально детально і зрозуміло)
        if pas in forbidden_passwords or len(pas) < criteria["min_length"]:
            status = "Заборонений"
            
        elif has_digit == True and has_upper == True and has_lower == True and has_special == True and len(pas) >= criteria["min_length"] + 4 and count_pass == 1:
            status = "Дуже сильний"
            
        elif has_digit == True and has_upper == True and has_lower == True and has_special == True and len(pas) < criteria["min_length"] + 4:
            status = "Сильний"
            
        elif (has_digit == True or has_upper == True or has_lower == True or has_special == True) and len(pas) >= criteria["min_length"]:
            status = "Середній"
            
        else:
            status = "Слабкий"
            
        # 5. Виводимо результат
        print(f"{pas:<25} | {status}")

# Запуск програми
if __name__ == "__main__":
    analyze_passwords()