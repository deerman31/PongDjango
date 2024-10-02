# game/middleware.py
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import jwt
from django.conf import settings

@database_sync_to_async
def get_user_from_token(token):
    from accounts.models import UserAccount
    try:
        decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = UserAccount.objects.get(id=decoded_data["user_id"])
        return user
    except:
        return AnonymousUser()

class QueryAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"].decode()
        query_params = dict(param.split('=') for param in query_string.split('&'))
        token = query_params.get("token")
        
        scope["user"] = await get_user_from_token(token) if token else AnonymousUser()
        return await super().__call__(scope, receive, send)