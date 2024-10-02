from rest_framework import serializers
from ..models import UserAccount
from typing import List, Dict, Any

import re
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

def is_alphanumeric(text):
    pattern = r'^[a-zA-Z0-9]+$'
    return bool(re.match(pattern, text))


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)

    class Meta:
        model: UserAccount = UserAccount
        fields: List[str] = ['name', 'email', 'password', 're_password']
    
    def validate_name(self, name) -> str:
        if not name:
            raise serializers.ValidationError("名前は必須です。")
        if UserAccount.objects.filter(name=name).exists():
            raise serializers.ValidationError("この名前は既に使用されています。")
        if UserAccount.objects.filter(email=name).exists():
            raise serializers.ValidationError("このメールアドレスは既に使用されています。")
        return name
    def validate_email(self, email) -> str:
        if not email:
            raise serializers.ValidationError("メールは必須です。")
        return email
    def validate_password(self, password) -> str:
        if not password:
            raise serializers.ValidationError("passwordは必須です。")
        try:
             validate_password(password)
        except ValidationError as e:
             raise serializers.ValidationError(e.message)
        return password
    def validate_re_password(self, re_password) -> str:
        if not re_password:
            raise serializers.ValidationError("re_passwordは必須です。")
        try:
             validate_password(re_password)
        except ValidationError as e:
             raise serializers.ValidationError(e.message)
        return re_password


    def validate(self, data: dict) -> dict:
        password = data['password']
        re_password = data['re_password']
    
        if password != re_password:
            raise serializers.ValidationError("パスワードが一致しません。")
        return data

    def create(self, validated_data: Dict[str, Any]) -> UserAccount:
        validated_data.pop('re_password')
        user: UserAccount = UserAccount.objects.create_user(
            name=validated_data['name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user