from rest_framework import serializers
from ovp.apps.users.validators import PasswordReuseInRecovery


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    class Meta:
        fields = ['token']
