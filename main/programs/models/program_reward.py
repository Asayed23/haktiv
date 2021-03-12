from django.utils.translation import gettext_lazy as _
from django.db import models
from django.conf import settings

from main.core.models import UniqueIdentityModel
from .program import Program


class ProgramReward(UniqueIdentityModel):
    class Meta:
        verbose_name = _("Program Reward")
        verbose_name_plural = _("Program Rewards")
    NA = "na"
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CRITERIA_CHOICES = (
        # (NA, _("N/A"),),
        (INFO, _("Info"),),
        (LOW, _("Low"),),
        (MEDIUM, _("Medium"),),
        (HIGH, _("High"),),
        (CRITICAL, _("Critical"),),
    )
    criteria = models.CharField(_("Reward Criteria"), max_length=24, choices=CRITERIA_CHOICES)
    swag     = models.CharField(_("Reward Swag"), max_length=200, null=True, blank=True)
    points   = models.PositiveIntegerField(_("Reward Points"), default=0)
    bounty   = models.FloatField(_("Reward Bounty"), default=0.0)
    program  = models.ForeignKey(Program, verbose_name=_("Program"), on_delete=models.CASCADE,
                                related_name='program_reward_program')

    def __str__(self):
        return f"{self.program.title} ({self.get_reward_type()})"

    def get_reward_type(self):
        return self.program.reward_type

    def get_reward_value(self):
        reward_type = self.get_reward_type()
        value = None
        if reward_type == Program.SWAG:
            value = self.swag
        elif reward_type == Program.POINTS:
            value = self.points
        elif reward_type == Program.BOUNTY:
            value = self.bounty
        return value

    @staticmethod
    def get_earned_points_variant(criteria, reward_type) -> int:
        reward_matrix = settings.REWARD_MATRIX[criteria]
        total_earned_points = 0
        if reward_type == Program.SWAG:
            total_earned_points = reward_matrix[Program.SWAG]
        elif reward_type == Program.POINTS:
            total_earned_points = reward_matrix[Program.POINTS]
        elif reward_type == Program.BOUNTY:
            total_earned_points = reward_matrix[Program.POINTS] + reward_matrix[Program.BOUNTY]
        return total_earned_points

    def get_earned_points(self) -> int:
        reward_type = self.get_reward_type()
        criteria = self.criteria
        return ProgramReward.get_earned_points_variant(criteria=criteria, reward_type=reward_type)

