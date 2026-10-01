from labs.lab01.task1 import analyze_passwords
from labs.lab01.task2 import check_access
from labs.lab01.task3 import secure_hashing_and_logging

def main():
    print(" ЗАВДАННЯ 1: АНАЛІЗАТОР ПАРОЛІВ ")
    analyze_passwords()
    
    print("\n ЗАВДАННЯ 2: СИСТЕМА КОНТРОЛЮ ДОСТУПУ ")
    check_access()
    
    print("\n ЗАВДАННЯ 3: БЕЗПЕЧНЕ ХЕШУВАННЯ ТА ЛОГУВАННЯ ")
    secure_hashing_and_logging()

if __name__ == "__main__":
    main()