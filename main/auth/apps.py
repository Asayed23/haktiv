from __future__ import unicode_literals, absolute_import

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class AuthConfig(AppConfig):
    name = "main.auth"
    verbose_name = _("Auth")