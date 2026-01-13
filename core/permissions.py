import jwt
from django.conf import settings
from rest_framework.permissions import BasePermission
from django.utils import timezone

from .models import User, Token, UserRole, Role, AccessRule, BusinessElement

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