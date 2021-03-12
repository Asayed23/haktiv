from django.db import models
from django.utils.translation import gettext_lazy as _

from main.core.models import UniqueIdentityModel
from .program import Program


class ProgramScope(UniqueIdentityModel):
    class Meta:
        verbose_name = _("Program Scope")
        verbose_name_plural = _("Program Scopes")
        ordering = ("-created",)

    IN_SCOPE = "in-scope"
    OUT_OF_SCOPE = "out-of-scope"

    SCOPE_STATUSES = (
        (IN_SCOPE, _("In-scope"),),
        (OUT_OF_SCOPE, _("Out-of-scope"),),
    )

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

    SCOPE_TYPES = (
        (WEB, _("Web"),),
        (IOS, _("iOS"),),
        (ANDROID, _("Android"),),
        (NETWORK, _("Network"),),
        (IOT, _("Internet of Things"),),
        (DESKTOP, _("Desktop"),),
        (SOURCE_CODE, _("Source Code"),),
    )

    program = models.ForeignKey(Program, verbose_name=_("Program"), on_delete=models.CASCADE,
                                related_name='program_scope_program')
    scope_type = models.CharField(_("Scope Type"), max_length=90, default=WEB, choices=SCOPE_TYPES)
    scope_status = models.CharField(_("Scope Status"), max_length=24, default=IN_SCOPE, choices=SCOPE_STATUSES)
    # is_eligible = models.BooleanField(_("Eligible Bounty"), default=False)
    in_scope_asset = models.CharField(_("In Scope Asset"), max_length=4000, default="Undefined")
    # out_scope_assets = models.TextField(_("Out of Scope Assets"), max_length=4000)
    # scope_description = models.TextField(_("Scope Description"), blank=True, null=True)

    def __str__(self):
        return f"{self.program.title} - {self.get_scope_type_display()} - {self.in_scope_asset}"
