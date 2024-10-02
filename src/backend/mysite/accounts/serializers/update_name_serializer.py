from rest_framework import serializers
from ..models import UserAccount
from django.core.exceptions import ValidationError
from accounts.models import validate_username

class UpdateNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['name']

    def validate_name(self, name):
        if not name:
            raise serializers.ValidationError("名前は必須です。")
        try:
            validate_username(name)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
        return name

    def validate(self, dict):
        name = dict["name"]
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError("認証されていないユーザーです。")

        if user.is_oauth:
            raise serializers.ValidationError("このユーザーは名前を変更できません。")
        if UserAccount.objects.filter(name=name).exists():
            raise serializers.ValidationError("この名前は既に使用されています。")
        return dict