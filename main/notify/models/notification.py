from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from main.core.models import UniqueIdentityModel


class Notification(UniqueIdentityModel):
    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ("-created",)

    GENERAL = "general"
    PROGRAM = "program"
    REPORT = "report"

    CATEGORIES = (
        (GENERAL, _("General"),),
        (PROGRAM, _("Program"),),
        (REPORT, _("Report"),),
    )

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("From User"), null=True, blank=True,
                                  related_name='from_user_notification', on_delete=models.SET_NULL)
    category = models.CharField(_("Category"), max_length=24, choices=CATEGORIES, default=GENERAL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE, related_name="to_user")
    read = models.BooleanField(_("Is read"), default=False)
    title = models.CharField(_("Title"), max_length=255)
    body = models.TextField(_("Description"))

    def __str__(self):
        return f"{self.category} - {self.title} - {self.user}"

    @classmethod
    def notify_user(cls, title, body, category=GENERAL, from_user=None, user=None):
        cls.objects.create(
            from_user=from_user,
            category=category,
            user=user,
            title=title,
            body=str(body),
        )
