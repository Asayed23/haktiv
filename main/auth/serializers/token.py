from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate

# from rest_framework_simplejwt.settings import api_settings
# from rest_framework_simplejwt.views import TokenViewBase
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.tokens import RefreshToken
# from drf_yasg.utils import swagger_auto_schema

from main.users.models import User
import time

class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('style', {})

        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True

        super().__init__(*args, **kwargs)


class TokenObtainSerializerBase(serializers.Serializer):
    email_field = User.EMAIL_FIELD

    default_error_messages = {
        'no_active_account': _('Wrong credentials')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.email_field] = serializers.EmailField(max_length=90, min_length=4, required=True)
        self.fields['password'] = PasswordField()

    def validate(self, attrs):
        authenticate_kwargs = {
            self.email_field: attrs[self.email_field],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        # Prior to Django 1.10, inactive users could be authenticated with the
        # default `ModelBackend`.  As of Django 1.10, the `ModelBackend`
        # prevents inactive users from authenticating.  App designers can still
        # allow inactive users to authenticate by opting for the new
        # `AllowAllUsersModelBackend`.  However, we explicitly prevent inactive
        # users from authenticating to enforce a reasonable policy and provide
        # sensible backwards compatibility with older Django versions.
        if self.user is None or not self.user.is_active:
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        return {}

    @classmethod
    def get_token(cls, user):
        raise NotImplementedError('Must implement `get_token` method for `TokenObtainSerializerBase` subclasses')


class TokenObtainPairSerializer(TokenObtainSerializerBase):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['token'] = str(refresh.access_token)

        return data


class HaktivTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['role'] = user.role
        token['godmod'] = user.is_staff
        token['has_2fa'] = user.has_2fa
        token["2fa_timestamp"] = time.time() if user.has_2fa else None
        return token
