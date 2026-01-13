# test_system_fixed.py
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_system():
    print("=== Тестирование системы аутентификации ===\n")
    
    # 1. Проверка доступности API
    print("1. Проверка доступности API...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            print(f"   Ответ: {response.json()}")
        else:
            print(f"   Ответ: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 2. Регистрация нового пользователя
    print("\n2. Регистрация пользователя...")
    try:
        response = requests.post(f"{BASE_URL}/register/", json={
            "email": "test_user@example.com",
            "first_name": "Тест",
            "last_name": "Пользователь",
            "password": "password123",  # 11 символов
            "password_confirm": "password123"  # 11 символов
        })
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ Пользователь зарегистрирован")
            user_data = response.json()
            token1 = user_data.get('token')
            print(f"   Токен получен: {'Да' if token1 else 'Нет'}")
        else:
            print(f"   ❌ Ошибка: {response.text}")
            return  # Прерываем тест, если регистрация не удалась
            
    except Exception as e:
        print(f"   Ошибка: {e}")
        return
    
    # 3. Вход в систему (получаем второй токен)
    print("\n3. Вход в систему...")
    try:
        response = requests.post(f"{BASE_URL}/login/", json={
            "email": "test_user@example.com",
            "password": "password123"
        })
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Вход успешен")
            token2 = response.json().get('token')
            print(f"   Токен: {token2[:20]}..." if token2 else "Нет токена")
            
            # 4. Проверка доступа к профилю с первым токеном
            print("\n4. Проверка доступа к профилю (первый токен)...")
            headers = {"Authorization": f"Bearer {token1}"}
            response = requests.get(f"{BASE_URL}/profile/", headers=headers)
            print(f"   Статус: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Доступ к профилю получен")
                print(f"   Данные: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            else:
                print(f"   ❌ Нет доступа: {response.text}")
            
            # 5. Проверка доступа с вторым токеном
            print("\n5. Проверка доступа к профилю (второй токен)...")
            headers = {"Authorization": f"Bearer {token2}"}
            response = requests.get(f"{BASE_URL}/profile/", headers=headers)
            print(f"   Статус: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Доступ к профилю получен")
            else:
                print(f"   ❌ Нет доступа: {response.text}")
                
        else:
            print(f"   ❌ Ошибка входа: {response.text}")
            
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 6. Проверка доступа без токена
    print("\n6. Проверка доступа без токена...")
    try:
        response = requests.get(f"{BASE_URL}/profile/")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Правильно требует аутентификацию")
        else:
            print(f"   Неожиданный статус: {response.status_code}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    print("\n=== Тестирование завершено ===")

if __name__ == "__main__":
    test_system()