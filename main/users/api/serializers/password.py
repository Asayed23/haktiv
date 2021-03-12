from django.utils.translation import ugettext as _
from rest_framework import serializers

import django.contrib.auth.password_validation as validators
from django.core import exceptions

from main.users.models import User

class UserResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=200)

class UserResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=200)
    password = serializers.CharField(min_length=8, max_length=200, style={"input_type": "password"})
    confirm_password = serializers.CharField(min_length=8, max_length=200, style={"input_type": "password"})
    def validate_email(self, email):
        if not User.objects.filter(email=email).first():
            raise serializers.ValidationError(dict(email=[_("Someone with that email address has already registered. Was it you?")]))
        return email
    def validate(self, data):
        if not data.get('password') or not data.get('confirm_password'):
            raise serializers.ValidationError(dict(password=[_("Please enter a password and confirm it.")]))

        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError(dict(password=[_("Those passwords don't match.")]))
        try:
            # validate the password and catch the exception
            validators.validate_password(password=data.get('password'), user=User)
        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(dict(password=list(e.messages)))
        return super(UserResetPasswordConfirmSerializer, self).validate(data)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8, max_length=200, style={"input_type": "password"})
    password = serializers.CharField(min_length=8, max_length=200, style={"input_type": "password"})
    confirm_password = serializers.CharField(min_length=8, max_length=200, style={"input_type": "password"})
    def validate(self, data):
        if not data.get('old_password'):
            raise serializers.ValidationError(dict(password=[_("Please enter a password and confirm it.")]))
        if not data.get('password') or not data.get('confirm_password'):
            raise serializers.ValidationError(dict(password=[_("Please enter a password and confirm it.")]))

        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError(dict(password=[_("Those passwords don't match.")]))
        try:
            # validate the password and catch the exception
            validators.validate_password(password=data.get('password'), user=User)
        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(dict(password=list(e.messages)))
        return super(UserResetPasswordConfirmSerializer, self).validate(data)