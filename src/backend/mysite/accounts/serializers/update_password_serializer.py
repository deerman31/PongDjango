from rest_framework import serializers
from ..models import UserAccount
from typing import List, Dict, Any
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class UpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    re_new_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserAccount
        fields: List[str] = ['new_password', 're_new_password', 'current_password']

    def validate(self, attrs):
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        re_new_password = attrs.get('re_new_password')

        if not all([current_password, new_password, re_new_password]):
            raise serializers.ValidationError("全ての入力欄を埋めてください。")
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError("認証されていないユーザーです。")
        if not user.check_password(current_password):
            raise serializers.ValidationError("現在のパスワードが正しくありません。")
        if new_password != re_new_password:
            raise serializers.ValidationError("新しいパスワードと確認用パスワードが一致しません。")
        if current_password == new_password:
            raise serializers.ValidationError("新しいパスワードは現在のパスワードと異なる必要があります。")
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
