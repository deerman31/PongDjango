import jwt
from rest_framework import authentication, exceptions
from django.conf import settings
from .models import UserAccount

class CustomJWTAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        try:
            # 'Bearer <token>'の形式になっているかチェック
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                raise exceptions.AuthenticationFailed('Authorization header must start with "Bearer".')
            
            # トークンをデコードしてペイロードを取得
            decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_payload.get('user_id')

            if not user_id:
                raise exceptions.AuthenticationFailed('Token payload missing user_id.')

            try:
                user = UserAccount.objects.get(id=user_id)
            except UserAccount.DoesNotExist:
                raise exceptions.AuthenticationFailed('User not found.')

            return (user, None)

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token.')

        return None