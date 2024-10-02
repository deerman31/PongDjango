from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import pyotp
import qrcode
from io import BytesIO
import base64
from django.contrib.auth import get_user_model
from rest_framework import status
import re

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_qr_code(request):
    user = request.user
    if user.is_2fa_enabled:
        #return Response({'detail': '2FA is already enabled'}, status=400)
        return Response({'detail': '2FA認証はすでに有効化されています。'}, status=400)
    if user.is_oauth == True:
        return Response({'detail': 'このユーザーは2FA認証はできません。'}, status=400)

    # if user.otp_secret:
    #     return Response({'detail': '2FA is already enabled'}, status=400)
    
    user.generate_otp_secret()
    otp_secret = user.otp_secret
    otp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(name=user.email, issuer_name="Your App Name")
    qr = qrcode.make(otp_uri)
    stream = BytesIO()
    qr.save(stream, 'PNG')
    qr_code = base64.b64encode(stream.getvalue()).decode()

    return Response({'qr_code': qr_code})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_otp(request):
    user = request.user
    otp = request.data.get('otp')
    otp_str = str(otp)
    if not bool(re.fullmatch(r'[0-9]+', otp_str)):
        return Response({'detail': '数字を入力せよ。'}, status=400)
    if len(otp_str) != 6:
        return Response({'detail': '数字は６桁です。'}, status=400)

    totp = pyotp.TOTP(user.otp_secret)

    if totp.verify(otp):
        user.is_2fa_enabled = True
        user.save()
        #return Response({'detail': '2FA setup complete.'})
        return Response({'detail': '2FA認証をセットアップしました。'}, status=200)
    else:
        #return Response({'detail': 'Invalid OTP code.'}, status=400)
        return Response({'detail': 'OTP codeが違います。'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    user = request.user
    if user.is_oauth == True:
        return Response({'detail': 'このユーザーは2FA認証はできません。'}, status=400)

    if user.is_2fa_enabled == False:
        #return Response({'detail': '2FA not enabled'}, )
        return Response({'detail': '2FA認証が有効になっていない。'}, status=status.HTTP_400_BAD_REQUEST)

    user.otp_secret = ''
    user.is_2fa_enabled = False
    user.save()
    return Response({'detail': '2FA認証を無効化にしました。'})

def otp_setup(request):
    return render(request, 'accounts/otp_setup.html')
