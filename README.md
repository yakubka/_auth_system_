# Система аутентификации и авторизации

## Описание системы доступа к ресурсам

### Схема базы данных

1. *users* - Пользователи системы
   - id (PK)
   - email (UNIQUE)
   - password_hash
   - first_name
   - last_name
   - patronymic
   - is_active
   - is_superuser
   - created_at
   - updated_at
   - deleted_at (мягкое удаление)

2. *roles* - Роли пользователей
   - id (PK)
   - name (UNIQUE)
   - description
   - created_at

3. user_roles- Связь пользователей и ролей
   - id (PK)
   - user_id (FK → users)
   - role_id (FK → roles)
   - created_at

4. business_elements - Бизнес-объекты системы
   - id (PK)
   - name (UNIQUE)
   - description
   - created_at

5. access_rules - Правила доступа
   - id (PK)
   - role_id (FK → roles)
   - element_id (FK → business_elements)
   - can_read (bool)
   - can_read_all (bool)
   - can_create (bool)
   - can_update (bool)
   - can_update_all (bool)
   - can_delete (bool)
   - can_delete_all (bool)
   - created_at
   - updated_at

6. tokens - Токены для JWT аутентификации
   - id (PK)
   - user_id (FK → users)
   - token
   - expires_at
   - is_active
   - created_at

Бизнес-объекты (Mock данные)
1. products - Товары
2. orders - Заказы
3. customers - Клиенты
4. suppliers - Поставщики
5. reports - Отчеты

 Роли по умолчанию
1. admin - Полный доступ ко всем ресурсам
2. manager - Доступ к товарам, заказам, клиентам
3. user - Базовый доступ к своему профилю и товарам
4. guest - Только просмотр товаров

*Как запустить*
 
 __git clone https://github.com/yakubka/_auth_system_.git__
 
 __cd имя дериктории__

 __python -m venv venv__

 
__chmod +x run.sh__


__./run.sh__
