from rest_framework import serializers
from ..models import UserAccount

class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['avatar']

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance