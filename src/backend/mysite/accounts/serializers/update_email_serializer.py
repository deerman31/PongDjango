from rest_framework import serializers
from ..models import UserAccount
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

class UpdateEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['email']

    def validate_email(self, email):
        if not email:
            raise serializers.ValidationError("メールアドレスは必須です。")

        validator = EmailValidator()
        try:
            validator(email)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
        if len(email) > 255:
            raise serializers.ValidationError("メールアドレスは255文字以下です")

        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError("認証されていないユーザーです。")
        if user.is_oauth:
            raise serializers.ValidationError("このユーザーはemailを変更できません。")
        if UserAccount.objects.filter(email=email).exists():
            raise serializers.ValidationError("このメールアドレスは既に使用されています。")
        return email