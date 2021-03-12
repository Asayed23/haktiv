from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate

import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.email)
        )

account_activation_token = AccountActivationTokenGenerator()

class IPVerifyTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.email) + six.text_type(user.role) + six.text_type(user.key)
        )

ip_token = IPVerifyTokenGenerator()

class RestPasswordTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.email) + six.text_type(user.role) + six.text_type(user.key) + six.text_type(user.email_verified) + 
            six.text_type(user.first_name) + six.text_type(user.last_name)
        )

reset_password_token = RestPasswordTokenGenerator()

class EmailActiveTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.email) + six.text_type(user.role) + six.text_type(user.key) + six.text_type(user.email_verified)
        )

email_active_token = EmailActiveTokenGenerator()
