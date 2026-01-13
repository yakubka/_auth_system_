from django.db import transaction
from .models import Role, BusinessElement, AccessRule, User, UserRole

def create_default_roles_and_elements():
    try:
        with transaction.atomic():
            roles_data = [
                {'name': 'admin', 'description': 'Администратор системы'},
                {'name': 'manager', 'description': 'Менеджер'},
                {'name': 'user', 'description': 'Обычный пользователь'},
                {'name': 'guest', 'description': 'Гость'},
            ]
            
            roles = {}
            for role_data in roles_data:
                role, created = Role.objects.get_or_create(
                    name=role_data['name'],
                    defaults=role_data
                )
                roles[role.name] = role
            
            elements_data = [
                {'name': 'products', 'description': 'Товары'},
                {'name': 'orders', 'description': 'Заказы'},
                {'name': 'customers', 'description': 'Клиенты'},
                {'name': 'suppliers', 'description': 'Поставщики'},
                {'name': 'reports', 'description': 'Отчеты'},
                {'name': 'users', 'description': 'Пользователи системы'},
                {'name': 'access_rules', 'description': 'Правила доступа'},
            ]
            
            elements = {}
            for element_data in elements_data:
                element, created = BusinessElement.objects.get_or_create(
                    name=element_data['name'],
                    defaults=element_data
                )
                elements[element.name] = element
            
           
            for element in elements.values():
                AccessRule.objects.get_or_create(
                    role=roles['admin'],
                    element=element,
                    defaults={
                        'can_read': True,
                        'can_read_all': True,
                        'can_create': True,
                        'can_update': True,
                        'can_update_all': True,
                        'can_delete': True,
                        'can_delete_all': True,
                    }
                )
            
            
            manager_elements = ['products', 'orders', 'customers', 'reports']
            for element_name in manager_elements:
                AccessRule.objects.get_or_create(
                    role=roles['manager'],
                    element=elements[element_name],
                    defaults={
                        'can_read': True,
                        'can_read_all': True,
                        'can_create': True,
                        'can_update': True,
                        'can_update_all': False,
                        'can_delete': True,
                        'can_delete_all': False,
                    }
                )
            
           
            user_elements = ['products', 'orders', 'customers']
            for element_name in user_elements:
                AccessRule.objects.get_or_create(
                    role=roles['user'],
                    element=elements[element_name],
                    defaults={
                        'can_read': True,
                        'can_read_all': False,
                        'can_create': False,
                        'can_update': False,
                        'can_update_all': False,
                        'can_delete': False,
                        'can_delete_all': False,
                    }
                )
            
            
            guest_elements = ['products']
            for element_name in guest_elements:
                AccessRule.objects.get_or_create(
                    role=roles['guest'],
                    element=elements[element_name],
                    defaults={
                        'can_read': True,
                        'can_read_all': False,
                        'can_create': False,
                        'can_update': False,
                        'can_update_all': False,
                        'can_delete': False,
                        'can_delete_all': False,
                    }
                )
            
            print("Система инициализирована успешно")
            return True
    except Exception as e:
        print(f"Ошибка при инициализации: {e}")
        return False