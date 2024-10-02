from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings
User = get_user_model()
from .login_view import get_first_error_message

def get_payload_from_expired_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        return payload.get("user_id")
        # return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

class LogoutView(APIView):
    authentication_classes = []  # ここで認証クラスを空に設定
    permission_classes = [AllowAny]
    #permission_classes = [IsAuthenticated]
    def post(self, request):

        if request.user.is_authenticated:
            user = request.user
            user.set_offline()
            return Response({"detail": "Logout successful."}, status=200)
        else:
            authorization_header = request.headers.get('Authorization')
            if authorization_header and authorization_header.startswith('Bearer '):
                access_token = authorization_header[7:]
            else:
                access_token = None
            if access_token:
                try:
                    user_id = get_payload_from_expired_token(access_token)
                    user = User.objects.get(id=user_id)
                    user.set_offline()
                    user.save()
                    return Response({"detail": "User set to offline."}, status=200)
                except (ValueError, User.DoesNotExist):
                    return Response({"detail": "Invalid access token or user does not exist."}, status=400)
            return Response({"detail": "Access token required."}, status=400)