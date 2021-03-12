from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import models

from main.core.models import UniqueIdentityModel

class UserTraffic(UniqueIdentityModel):
    class Meta:
        verbose_name = _("User Traffic")
        verbose_name_plural = _("User Traffics")
        ordering = ("-created",)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_traffic_user")
    visitor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True,
                                related_name="user_traffic_visitor")
    count = models.PositiveIntegerField(_('Visit Count'), default=1)

    def __str__(self):
        return f"{self.user.get_short_name} - {self.count} visits."

    @staticmethod
    def get_visit_latest(user):
        visitor = UserTraffic.objects.filter(user=user).last()
        return visitor.created.isoformat() if visitor else None

    @staticmethod
    def get_visit_count(user):
        return UserTraffic.objects.filter(user=user).count()

    @staticmethod
    def register_visit(user, visitor):
        obj, created = None, True
        if user != visitor:
            obj, created = UserTraffic.objects.get_or_create(user=user, visitor=visitor)
            if not created:
                obj.count = obj.count + 1
                obj.save()
        return obj, created
