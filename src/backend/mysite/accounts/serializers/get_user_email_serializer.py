from rest_framework import serializers
from ..models import UserAccount

class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['email']