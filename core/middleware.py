import jwt
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import Token, User

class JWTAuthenticationMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                
               
                if timezone.datetime.fromtimestamp(payload['exp'], tz=timezone.utc) < timezone.now():
                    request.user = None
                    return
                
                user_id = payload['user_id']
                
                
                db_token = Token.objects.filter(
                    user_id=user_id,
                    token=token,
                    is_active=True,
                    expires_at__gt=timezone.now()
                ).first()  
                
                if db_token:
                    user = User.objects.get(id=user_id, is_active=True)
                    request.user = user
                else:
                    request.user = None
                    
            except jwt.ExpiredSignatureError:
                request.user = None
            except jwt.InvalidTokenError:
                request.user = None
            except User.DoesNotExist:
                request.user = None
            except Exception as e:
                
                print(f"Auth middleware error: {e}")
                request.user = None
        else:
            request.user = None