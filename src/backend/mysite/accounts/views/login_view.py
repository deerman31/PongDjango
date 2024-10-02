from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from typing import Any, Dict
import json

from ..serializers.login_serializer import LoginSerializer

import jwt
import datetime
from django.conf import settings
import os

class LoginView(APIView):
    authentication_classes = []  # 認証を無効にする

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # print("--------------Headers----------------")
        # for h,v in request.headers.items():
        #     print(f"{h}: {v}")
        # print("--------------Headers----------------")

        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
             # 2FAが必要かどうかをチェック
            if serializer.validated_data.get('two_fa_required'):
                return Response({
                    'detail': '二段階認証が必要です。OTPコードを入力してください。',
                    'two_fa_required': True
                }, status=status.HTTP_401_UNAUTHORIZED)
                

            # 現在のUTC時刻を取得
            current_time = datetime.datetime.now(datetime.timezone.utc)

            # トークンのペイロード設定
            # 環境変数から値を取得し、適切な型に変換
            # 環境変数からトークンの有効期限を取得し、デフォルト値を設定
            access_token_exp_minutes = int(os.getenv('ACCESS_TOKEN_VALUE', '5'))  # デフォルトは5分
            refresh_token_exp_days = int(os.getenv('REFRESH_TOKEN_VALUE', '7'))  # デフォルトは7日

            access_token_payload: Dict[str, Any] = {
                'user_id': user.id,
                #'exp': current_time + datetime.timedelta(minutes=5),  # 有効期限5分
                'exp': current_time + datetime.timedelta(minutes=access_token_exp_minutes),
                #'exp': current_time + datetime.timedelta(minutes=os.getenv('ACCESS_TOKEN_VALUE')),  # 有効期限5分
                'iat': current_time,  # 発行時間
            }
            
            refresh_token_payload: Dict[str, Any] = {
                'user_id': user.id,
                #'exp': current_time + datetime.timedelta(days=7),  # 有効期限7日
                'exp': current_time + datetime.timedelta(days=refresh_token_exp_days),
                #'exp': current_time + datetime.timedelta(days=os.getenv('REFRESH_TOKEN_VALUE')),  # 有効期限7日
                'iat': current_time,
            }

            # トークンの生成
            access_token: str = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')
            refresh_token: str = jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')

            #refresh = RefreshToken.for_user(user)

            return Response({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_200_OK)

        error_message = get_first_error_message(serializer.errors)
        return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

def get_first_error_message(serializer_errors):
    """シリアライザーのエラーから最初のエラーメッセージを抽出する"""
    errors = list(serializer_errors.values())
    if errors:
        first_error = errors[0]
        if isinstance(first_error, list) and first_error:
            return str(first_error[0])
    return "エラーが発生しました"  # デフォルトのエラーメッセージ