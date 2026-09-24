from task1 import analyze_passwords
from task2 import check_access
from task3 import task3

def main():
    print("=== ЗАВДАННЯ 1: АНАЛІЗАТОР ПАРОЛІВ ===")
    analyze_passwords()
    
    print("\n=== ЗАВДАННЯ 2: СИСТЕМА КОНТРОЛЮ ДОСТУПУ ===")
    check_access()
    
    print("\n=== ЗАВДАННЯ 3: БЕЗПЕЧНЕ ХЕШУВАННЯ ТА ЛОГУВАННЯ ===")
    task3()

if __name__ == "__main__":
    main()