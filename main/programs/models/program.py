# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.db.models import Max, Sum, Value as V
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from main.core.models import UniqueIdentityModel
from .program_tag import ProgramTypeTag


class Program(UniqueIdentityModel):
    """
# Program Reward:
## Bountry:
Money would be added to user’s profile for each accepted report dependent on its severity & shall also have
an equivalent number of points added to researcher’s profile
## Points:
only points would be added to user’s profile
## Swag:
giveaways would be sent to researchers via customer & shall also have an equivalent number of points added
to researcher’s profile
"""

    class Meta:
        verbose_name = _("Program")
        verbose_name_plural = _("Programs")
        ordering = ("-created",)

    BOUNTY = "bounty"
    POINTS = "points"
    SWAG = "swag"

    REWARD_TYPES = (
        (BOUNTY, _("Bounty"),),
        (POINTS, _("Points"),),
        (SWAG, _("Swag"),),
    )

    PUBLIC = "public"
    PRIVATE = "private"
    VISIBILITIES = (
        (PUBLIC, _("Public"),),
        (PRIVATE, _("Private"),),
    )

    INACTIVE = "inactive"
    ACTIVE = "active"
    STATUSES = (
        (INACTIVE, _("Inactive"),),
        (ACTIVE, _("Active"),),
    )

    sequence_id = models.CharField(_("Sequence ID"), max_length=200, )
    reward_type = models.CharField(_("Reward Type"), max_length=24, default=SWAG, choices=REWARD_TYPES)

    # Program info
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Program Manager"),
                                 null=True, blank=True, related_name='program_customer', on_delete=models.SET_NULL)
    triagers = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Assigned Triagers"), blank=True,
                                      related_name='program_triagers')
    status = models.CharField(_("Program Status"), max_length=24, choices=STATUSES, default=INACTIVE)
    visibility = models.CharField(_("Program Visibility"), max_length=24, choices=VISIBILITIES, default=PRIVATE)
    logo = models.ForeignKey(settings.MEDIA_FILEMANAGER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                             related_name="program_logo")
    title = models.CharField(_("Program Title"), max_length=255)
    slug = AutoSlugField(populate_from='title', unique=True)
    website = models.URLField(_("Website"))
    bio = models.TextField(_("Program Biography"))
    tags = models.ManyToManyField(ProgramTypeTag, verbose_name=_("Program Type Tags"), related_name='program_tags')

    policy = models.TextField(_("Program Policy"))
    launch_date = models.DateField(_("Launch Date"))
    end_date = models.DateField(_("End Date"), blank=True, null=True)
    scope_description = models.TextField(_("Scope Description"))
    out_scope_asset = models.TextField(_("Out of Scope Asset"), max_length=4000, blank=True, null=True)

    hackers = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Hackers"), blank=True,
                                     related_name="program_hackers", )

    def __str__(self):
        return f"{self.title}"

    @property
    def submitted_reports(self) -> int:
        """Total number of reports submitted"""
        from .program_report import ProgramReport
        return ProgramReport.objects.filter(program=self).count()

    @property
    def accepted_reports(self) -> int:
        """Total number of accepted reports (pending reward)"""
        from .program_report import ProgramReport
        return ProgramReport.objects.filter(program=self,
                                            category__in=[ProgramReport.PENDING, ProgramReport.APPROVED]).count()

    @property
    def rewarded_reports(self) -> int:
        """Total number of rewarded reports"""
        from .program_report_reward import ProgramReportReward
        return ProgramReportReward.objects.filter(report__program=self).count()

    @property
    def last_submitted_date(self) -> timezone.datetime:
        """Last submitted report date"""
        from .program_report import ProgramReport
        program_report = ProgramReport.objects.filter(program=self).last()
        return program_report.created if program_report else timezone.now()

    @property
    def paid_bounties(self) -> float:
        """Total bounties paid in USD"""
        from .program_report_reward import ProgramReportReward
        program_report_rewards = ProgramReportReward.objects.filter(report__program=self)\
            .aggregate(bounty=Coalesce(Sum("bounty"), V(0)))
        return program_report_rewards["bounty"]

    @property
    def days_since_report_solved(self) -> int:
        """Number of days since last report was resolved"""
        # DEPRECATED: No update
        return 20

    def get_statistics(self):
        return dict(
            submitted_reports=self.submitted_reports,
            accepted_reports=self.accepted_reports,
            rewarded_reports=self.rewarded_reports,
            last_submitted_date=self.last_submitted_date,
            paid_bounties=self.paid_bounties,
            days_since_report_solved=self.days_since_report_solved,
        )

    @property
    def reports(self):
        return []

    @property
    def hof(self):
        from .program_hof import ProgramHallOfFame
        return ProgramHallOfFame.objects.filter(program=self)

    def hall_of_fame(self):
        return self.hof

    hall_of_fame.short_description = _("Hall Of Fame")

    def program_reward(self):
        from .program_reward import ProgramReward
        return ProgramReward.objects.filter(program=self)

    def program_scopes(self):
        from .program_scope import ProgramScope
        return ProgramScope.objects.filter(program=self)

    def get_next_id(self):
        default_start = 23
        id_max = Program.objects.aggregate(Max('id'))["id__max"]
        return id_max + default_start if id_max else default_start
