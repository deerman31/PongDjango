from rest_framework import serializers
from django.contrib.auth import authenticate
from ..models import UserAccount
import pyotp
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from typing import List, Dict, Any
from accounts.models import validate_username
from django.core.validators import EmailValidator
import re

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # nameかemailを受け取る
    password = serializers.CharField(write_only=True)
    otp = serializers.CharField(required=False)

    class Meta:
        model = UserAccount
        fields: List[str] = ['identifier', 'password']

    def validate_identifier(self, value: str) -> str:
        if '@' in value:
            validator = EmailValidator()
            try:
                validator(value)
            except ValidationError as e:
                raise serializers.ValidationError(e.message)
            if len(value) > 255:
                raise serializers.ValidationError("メールアドレスは255文字以下です")
        else:
            try:
                validate_username(value)
            except ValidationError as e:
                raise serializers.ValidationError(e.message)
        return value

    def validate(self, data: dict) -> dict:
        identifier: str = data.get('identifier')
        password: str = data.get('password')

        # 最初にidentifierとpasswordの存在チェック
        if not identifier or not password:
            raise serializers.ValidationError("メールアドレス/名前とパスワードは必須です。")

        try:
            validate_password(password, self.instance)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        try:
            if '@' in identifier:
                user: UserAccount = UserAccount.objects.get(email__iexact=identifier)
            else:
                user: UserAccount = UserAccount.objects.get(name__iexact=identifier)
        except UserAccount.DoesNotExist:
            raise serializers.ValidationError("無効なメールアドレスまたは名前です。")

        # 認証をemailで行う
        user = authenticate(request=self.context.get('request'), email=user.email, password=password)
        if user is None:
            raise serializers.ValidationError("メールアドレスまたはパスワードが正しくありません。")
        if not user.is_active:
            raise serializers.ValidationError("このアカウントは無効です。")

        if user.is_2fa_enabled:
            otp = data.get('otp')
            if not otp:
                data['two_fa_required'] = True
            else:
                otp_str = str(otp)
                if not bool(re.fullmatch(r'[0-9]+', otp_str)):
                    raise serializers.ValidationError('数字を入力せよ。')
                if len(otp_str) != 6:
                    raise serializers.ValidationError('数字は６桁です。')
                totp = pyotp.TOTP(user.otp_secret)
                if not totp.verify(otp):
                    raise serializers.ValidationError('OTP codeが違います。')
                data['two_fa_required'] = False
        else:
            data['two_fa_required'] = False

        data['user'] = user
        user.set_online()
        return data
