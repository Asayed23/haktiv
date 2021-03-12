from django.utils.translation import ugettext as _
from rest_framework import serializers
from main.users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model =User
        fields = '__all__'

class TwoFactorSerializer(serializers.Serializer):
    otp = serializers.RegexField(label=_("OTP Code"), regex=r"^\d{6}$", help_text=_("Only 6 Digits OTP Code Allowed"))