# accounts/views/oauth_views.py

import requests
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import datetime
import jwt
import os

User = get_user_model()

class OauthLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        authorization_url = (
            f"{settings.AUTHORIZATION_BASE_URL}"
            f"?client_id={settings.CLIENT_ID}"
            f"&redirect_uri={settings.REDIRECT_URI}"
            f"&response_type=code"
        )
        return redirect(authorization_url)

class CallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        if code is None:
            return render(request, 'accounts/error.html', {'message': 'No code provided'})
        
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.REDIRECT_URI,
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
        }
        
        token_response = requests.post(settings.TOKEN_URL, data=token_data)
        token_json = token_response.json()
        
        #print("token_json:", token_json)
        access_token = token_json.get('access_token')
        if not access_token:
            return render(request, 'accounts/error.html', {'message': 'Failed to obtain access token'})

        user_info_response = requests.get(
            'https://api.intra.42.fr/v2/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_info = user_info_response.json()
        
        email = user_info['email']
        username = user_info['login']

        
        if User.objects.filter(name=username, is_oauth=False).exists():
            return render(request, 'accounts/error.html', {'message': "同じユーザー名のユーザーがいるため、サインアップできません"})

        if User.objects.filter(email=email, is_oauth=False).exists():
            return render(request, 'accounts/error.html', {'message': "同じメールアドレスのユーザーがいるため、サインアップできません"})

        # ユーザーの存在確認と作成
        user, created = User.objects.get_or_create(email=email, defaults={'name': username, 'is_oauth': True})
        
        if created:
            user.set_unusable_password()  # パスワードを無効化
            user.save()

        # DEBUG ここでuserのクラス変数をすべて出力する
        # print(vars(user))
                    # 現在のUTC時刻を取得
        current_time = datetime.datetime.now(datetime.timezone.utc)
        access_token_exp_minutes = int(os.getenv('ACCESS_TOKEN_VALUE', '5'))  # デフォルトは5分
        refresh_token_exp_days = int(os.getenv('REFRESH_TOKEN_VALUE', '7'))  # デフォルトは7日

        # トークンのペイロード設定
        access_token_payload = {
            'user_id': user.id,
            'exp': current_time + datetime.timedelta(minutes=access_token_exp_minutes),
            'iat': current_time,  # 発行時間
        }
        
        refresh_token_payload = {
            'user_id': user.id,
            'exp': current_time + datetime.timedelta(days=refresh_token_exp_days),
            'iat': current_time,
        }
        # トークンの生成
        access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')
        refresh_token = jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')

        
        user.set_online()

        # JWTトークンをクライアントに返す
        return render(request, 'accounts/profile.html', {
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
        })
