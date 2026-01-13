from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, BasePermission
import jwt
from django.conf import settings
from django.utils import timezone

from .models import User, Role, UserRole, Token, BusinessElement, AccessRule
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    RoleSerializer,
    BusinessElementSerializer,
    AccessRuleSerializer,
    UserRoleSerializer
)

# ================ ПЕРМИШЕНЫ ================

class IsAuthenticated(BasePermission):
    
    
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            if timezone.datetime.fromtimestamp(payload['exp'], tz=timezone.utc) < timezone.now():
                return False
            
            user_id = payload['user_id']
            db_token = Token.objects.filter(
                user_id=user_id,
                token=token,
                is_active=True,
                expires_at__gt=timezone.now()
            ).first()
            
            if not db_token:
                return False
            
            user = User.objects.get(id=user_id, is_active=True)
            request.user = user  
            
            return True
            
        except Exception:
            return False

class HasPermission(BasePermission):
    
    def __init__(self, element_name=None, action='read'):
        self.element_name = element_name
        self.action = action
    
    def has_permission(self, request, view):
        if not hasattr(request, 'user') or not request.user:
            return False
        
        if request.user.is_superuser:
            return True
        
        if not self.element_name:
            return True
        
        try:
            element = BusinessElement.objects.get(name=self.element_name)
            user_roles = UserRole.objects.filter(user=request.user).select_related('role')
            
            for user_role in user_roles:
                try:
                    access_rule = AccessRule.objects.get(role=user_role.role, element=element)
                    
                    if self.action == 'read':
                        return access_rule.can_read
                    elif self.action == 'create':
                        return access_rule.can_create
                    elif self.action == 'update':
                        return access_rule.can_update
                    elif self.action == 'delete':
                        return access_rule.can_delete
                except AccessRule.DoesNotExist:
                    continue
            
            return False
            
        except BusinessElement.DoesNotExist:
            return False


class CanReadProducts(HasPermission):
    def __init__(self):
        super().__init__(element_name='products', action='read')

class CanReadOrders(HasPermission):
    def __init__(self):
        super().__init__(element_name='orders', action='read')

class CanReadCustomers(HasPermission):
    def __init__(self):
        super().__init__(element_name='customers', action='read')

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request, 'user') and request.user and request.user.is_superuser

# ================ VIEWS АУТЕНТИФИКАЦИИ ================

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            try:
                user_role = Role.objects.get(name='user')
                UserRole.objects.create(user=user, role=user_role)
            except Role.DoesNotExist:
                pass
            
            token = user.generate_token()
            
            return Response({
                'token': token,
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(email=email, is_active=True)
                
                if user.check_password(password):
                    token = user.generate_token()
                    
                    return Response({
                        'token': token,
                        'user': {
                            'id': str(user.id),
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name
                        }
                    })
                else:
                    return Response(
                        {'error': 'Неверный email или пароль'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
            except User.DoesNotExist:
                return Response(
                    {'error': 'Неверный email или пароль'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Получение профиля пользователя"""
        user = request.user
        return Response({
            'success': True,
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'patronymic': user.patronymic,
                'created_at': user.created_at,
                'is_active': user.is_active,
                'is_superuser': user.is_superuser
            }
        })
    
    def patch(self, request):

        user = request.user
        
        data = request.data
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'patronymic' in data:
            user.patronymic = data['patronymic']
        
        user.save()
        
        return Response({
            'success': True,
            'message': 'Профиль обновлен',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'patronymic': user.patronymic,
                'created_at': user.created_at
            }
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                db_token = Token.objects.filter(token=token, user=request.user, is_active=True).first()
                if db_token:
                    db_token.is_active = False
                    db_token.save()
            except Token.DoesNotExist:
                pass
        
        return Response({'message': 'Успешный выход из системы'})

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        user = request.user
        user.is_active = False
        user.deleted_at = timezone.now()
        user.save()
        
        Token.objects.filter(user=user, is_active=True).update(is_active=False)
        
        return Response({'message': 'Аккаунт успешно удален'})

# ================ MOCK БИЗНЕС-ОБЪЕКТЫ ================

class ProductsView(APIView):
    permission_classes = [IsAuthenticated, CanReadProducts]
    
    def get(self, request):
        return Response({
            'message': 'Доступ к товарам разрешен',
            'user': request.user.email,
            'data': [
                {'id': 1, 'name': 'Товар 1', 'price': 100, 'owner': str(request.user.id)},
                {'id': 2, 'name': 'Товар 2', 'price': 200, 'owner': str(request.user.id)},
                {'id': 3, 'name': 'Товар 3', 'price': 300, 'owner': 'admin_id'},
            ]
        })

class OrdersView(APIView):
    permission_classes = [IsAuthenticated, CanReadOrders]
    
    def get(self, request):
        return Response({
            'message': 'Доступ к заказам разрешен',
            'user': request.user.email,
            'data': [
                {'id': 1, 'product': 'Товар 1', 'quantity': 2, 'owner': str(request.user.id)},
                {'id': 2, 'product': 'Товар 2', 'quantity': 1, 'owner': 'admin_id'},
            ]
        })

class CustomersView(APIView):
    permission_classes = [IsAuthenticated, CanReadCustomers]
    
    def get(self, request):
        return Response({
            'message': 'Доступ к клиентам разрешен',
            'user': request.user.email,
            'data': [
                {'id': 1, 'name': 'Иван Иванов', 'email': 'ivan@example.com', 'owner': str(request.user.id)},
                {'id': 2, 'name': 'Петр Петров', 'email': 'petr@example.com', 'owner': 'admin_id'},
            ]
        })

# ================ АДМИНСКИЕ VIEWSETS ================

class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class AccessRuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer

class BusinessElementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer

class UserRoleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer

# ================ СИСТЕМНЫЕ VIEWS ================

class InitializeSystemView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Инициализация системы: создание стандартных ролей и элементов"""
        from .utils import create_default_roles_and_elements
        
        try:
            create_default_roles_and_elements()
            
            
            if not User.objects.filter(email='admin@example.com').exists():
                admin_user = User.objects.create(
                    email='admin@example.com',
                    first_name='Администратор',
                    last_name='Системы'
                )
                admin_user.set_password('admin123')
                admin_user.is_superuser = True
                admin_user.is_staff = True
                admin_user.save()
                
                try:
                    admin_role = Role.objects.get(name='admin')
                    UserRole.objects.create(user=admin_user, role=admin_role)
                except Role.DoesNotExist:
                    pass
            
            return Response({'message': 'Система инициализирована успешно'})
        except Exception as e:
            return Response(
                {'error': f'Ошибка инициализации: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class APIRootView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'system': 'Система аутентификации и авторизации',
            'version': '1.0',
            'endpoints': {
                'auth': {
                    'register': 'POST /api/register/',
                    'login': 'POST /api/login/',
                    'logout': 'POST /api/logout/',
                    'profile': 'GET /api/profile/',
                    'delete-account': 'DELETE /api/delete-account/',
                },
                'business_objects': {
                    'products': 'GET /api/products/',
                    'orders': 'GET /api/orders/',
                    'customers': 'GET /api/customers/',
                },
                'system': {
                    'init': 'POST /api/init/',
                },
                'admin': {
                    'roles': 'GET /api/admin/roles/',
                    'access-rules': 'GET /api/admin/access-rules/',
                    'elements': 'GET /api/admin/elements/',
                    'user-roles': 'GET /api/admin/user-roles/',
                }
            }
        })