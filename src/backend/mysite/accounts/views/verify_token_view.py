from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from rest_framework.request import Request
from typing import Any, Dict

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class VerifyTokenView(APIView):
    permission_classes = []

    def post(self, request: Request, *args: Any, **kwargs: Any):
        token: str = request.data.get('access_token')

        if not token:
            return Response({"detail": "トークンが提供されていません。"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # トークンをデコードして検証
            decoded_token: str = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_exp": True})
            return Response({"detail": "トークンは有効です。"}, status=status.HTTP_200_OK)

        except ExpiredSignatureError:
            # トークンが期限切れの場合
            return Response({"detail": "トークンの有効期限が切れています。"}, status=status.HTTP_401_UNAUTHORIZED)
        except InvalidTokenError:
            # トークンが無効な場合
            return Response({"detail": "無効なトークンです。"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            # 予期しないエラーの場合
            return Response({"detail": f"予期しないエラーが発生しました: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)