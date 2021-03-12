# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings
from django.utils import timezone

from main.core.models import TimeStampedModel

class PasswordHistory(TimeStampedModel):
    class Meta:
        verbose_name = _("Password History")
        verbose_name_plural = _("Password Histories")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    password = models.CharField(verbose_name=_("Encrypted Password"), max_length=240)

    def get_dict(self):
        return dict(
            id=self.id,
            user=dict(pk=self.user.pk, full_name=self.user.get_full_name()),
            password=self.password,
        )
    def __str__(self):
        return self.user.get_full_name()

    def since_days(self):
        # Get Days Count
        return (timezone.now() - self.created).days