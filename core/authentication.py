import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from .models import User, Token

class JWTAuthentication(authentication.BaseAuthentication):
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            
            if timezone.datetime.fromtimestamp(payload['exp'], tz=timezone.utc) < timezone.now():
                raise AuthenticationFailed('Token expired')
            
            user_id = payload['user_id']
            
           
            db_token = Token.objects.filter(
                user_id=user_id,
                token=token,
                is_active=True,
                expires_at__gt=timezone.now()
            ).first()
            
            if not db_token:
                raise AuthenticationFailed('Invalid token')
            
            
            try:
                user = User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                raise AuthenticationFailed('User not found')
            
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')