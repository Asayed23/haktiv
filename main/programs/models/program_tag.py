from django.db import models
from django.utils.translation import gettext_lazy as _


class ProgramTypeTag(models.Model):
    class Meta:
        verbose_name = _("Program Type Tag")
        verbose_name_plural = _("Program Type Tags")

    WEB = "WEB"
    IOS = "IOS"
    ANDROID = "ANDROID"
    NETWORK = "NETWORK"
    IOT = "IOT"
    DESKTOP = "DESKTOP"
    SOURCE_CODE = "SOURCE_CODE"

    # API = "API"  # REMOVED
    # MOBILE = "MOBILE"  # REMOVED
    # HOST = "HOST"  # REMOVED
    # HARDWARE = "HARDWARE"  # REMOVED
    # OTHER = "OTHER"  # REMOVED

    PROGRAM_TYPE_TAGS = (
        (WEB, _("Web"),),
        (IOS, _("iOS"),),
        (ANDROID, _("Android"),),
        (NETWORK, _("Network"),),
        (IOT, _("Internet of Things"),),
        (DESKTOP, _("Desktop"),),
        (SOURCE_CODE, _("Source Code"),),
    )

    name = models.CharField(_("Name"), max_length=90, default=WEB, choices=PROGRAM_TYPE_TAGS)

    @classmethod
    def load_default(cls):
        for name in cls.PROGRAM_TYPE_TAGS:
            obj, created = cls.objects.get_or_create(name=name[0])
            print(obj, created)

    def __str__(self):
        return f"{self.get_name_display()}"
