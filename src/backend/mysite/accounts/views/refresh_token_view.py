import jwt
import datetime
from jwt import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from typing import Any, Dict

class RefreshTokenView(APIView):
    def post(self, request: Request, *args: Any, **kwargs: Any):
        refresh_token: str = request.data.get('refresh_token')

        if not refresh_token:
            return Response({"detail": "リフレッシュトークンが提供されていません。"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # リフレッシュトークンのデコードと検証
            decoded_token: str = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])

            # 現在のUTC時刻を取得
            current_time = datetime.datetime.now(datetime.timezone.utc)
            # 新しいアクセストークンの発行
            new_access_token_payload: Dict[str, Any] = {
                'user_id': decoded_token['user_id'],
                # 'exp': current_time + datetime.timedelta(minutes=5),
                'exp': current_time + datetime.timedelta(seconds=10),
                'iat': current_time
            }

            new_access_token: str = jwt.encode(new_access_token_payload, settings.SECRET_KEY, algorithm="HS256")

            return Response({
                'access_token': new_access_token
            }, status=status.HTTP_200_OK)
        
        except ExpiredSignatureError:
            return Response({"detail": "リフレッシュトークンの有効期限が切れています。"}, status=status.HTTP_401_UNAUTHORIZED)
        
        except InvalidTokenError:
            return Response({"detail": "無効なリフレッシュトークンです。"}, status=status.HTTP_401_UNAUTHORIZED)