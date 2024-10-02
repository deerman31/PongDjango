from rest_framework import serializers
from ..models import UserAccount
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class DeleteUserSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserAccount
        field = ['current_password']


    def validate(self, attrs):
        current_password = attrs.get('current_password')

        if not current_password:
            raise serializers.ValidationError("パスワードは必須です。")
        try:
            validate_password(current_password, self.instance)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(str(e))

        user = self.instance
        if user is None:
            raise serializers.ValidationError("ユーザーが存在しません。")

        # 現在のpasswordが正しいか確認
        if not check_password(current_password, user.password):
            raise serializers.ValidationError("現在のパスワードが正しくありません。")

        return attrs