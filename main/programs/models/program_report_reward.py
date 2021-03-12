from django.conf import settings
from django.db import models
from django.db.models import Sum, Value as V
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
import datetime

from main.core.models import UniqueIdentityModel
from .program import Program
from .program_report import ProgramReport
from .program_reward import ProgramReward

def get_past_month_range() -> tuple:
    today = datetime.date.today()
    start = today.replace(day=1)
    past_month_end = start - timezone.timedelta(days=1)
    past_month_start = past_month_end.replace(day=1)
    past_month_end = past_month_end
    return past_month_start, past_month_end

def get_second_past_month_range() -> tuple:
    past_month_start, past_month_end = get_past_month_range()
    second_past_month_end = past_month_start - timezone.timedelta(days=1)
    second_past_month_start = second_past_month_end.replace(day=1)
    return second_past_month_start, second_past_month_end

def get_past_month_days_list() -> list:
    today = datetime.date.today()
    start = today.replace(day=1)
    past_last_date = start - timezone.timedelta(days=1)
    length = past_last_date.day
    date_range = [past_last_date - datetime.timedelta(days=x) for x in range(length)]
    return date_range

def get_12_months_list() -> list:
    today = datetime.date.today()
    next_month = today.month % 12 if today.month != 12 else 12
    start = today.replace(year=today.year - 1).replace(month=next_month).replace(day=1)
    date_range = [start.replace(month=x % 12 if x != 12 else 12) for x in range(1, 13)]
    return date_range

class ProgramReportRewardManager(models.Manager):
    pass

class ProgramReportRewardQuerySet(models.QuerySet):
    def upcoming_payments(self):
        # rewards not paid yet
        return self.filter(is_paid=False)
    def completed_payments(self):
        # rewards paid to researcher
        return self.filter(is_paid=True)

    def completed_payments_12_month(self):
        today = timezone.datetime.now()
        before12month = today.replace(year=today.year - 1) + timezone.timedelta(days=1)
        return self.completed_payments().filter(paid_at__range=[before12month, today])

    def past_month_payments(self):
        # rewards gained past month
        return self.filter(paid_at__range=get_past_month_range())

    def second_past_month_payments(self):
        # rewards gained second past month
        return self.filter(paid_at__range=get_second_past_month_range())

class ProgramReportReward(UniqueIdentityModel):
    class Meta:
        verbose_name = _("Program Report Reward")
        verbose_name_plural = _("Program Report Rewards")
        ordering = ("-created",)

    SPECIAL_ORDER_BY = {
        "created": "created",
        "-created": "-created",
        "modified": "modified",
        "-modified": "-modified",
        "sequence_id": "report__sequence_id",
        "-sequence_id": "-report__sequence_id",
        "bounty": "bounty",
        "-bounty": "-bounty",
    }
    UPCOMING = "upcoming"
    PAST_MONTH = "past_month"
    COMPLETED = "completed"

    AVAILABLE_SCOPES = [UPCOMING, PAST_MONTH, COMPLETED]
    DEFAULT_SCOPE = UPCOMING

    BOUNTY = Program.BOUNTY
    SWAG = Program.SWAG
    POINTS = Program.POINTS
    REWARD_TYPES = Program.REWARD_TYPES

    CRITERIA_CHOICES = ProgramReward.CRITERIA_CHOICES

    objects = ProgramReportRewardManager.from_queryset(ProgramReportRewardQuerySet)()

    criteria = models.CharField(_("Reward Criteria"), max_length=24, choices=CRITERIA_CHOICES, default=ProgramReward.NA)
    reward_type = models.CharField(_("Reward Type"), max_length=24, choices=REWARD_TYPES, default=POINTS)
    swag = models.CharField(_("Reward Swag"), max_length=200, null=True, blank=True)
    points = models.PositiveIntegerField(_("Reward Points"), default=0)
    bounty = models.FloatField(_("Reward Bounty"), default=0.0)
    report = models.OneToOneField(ProgramReport, verbose_name=_("Program Report"), on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Researcher"), on_delete=models.CASCADE,
                             help_text=_("In this case user can be researcher or triager"))
    is_paid = models.BooleanField(_("Is Paid"), default=False)
    paid_at = models.DateTimeField(_("Paid At"), blank=True, null=True)
    payment_note = models.TextField(_("Payment Note"), blank=True, help_text=_("This is internal payment note (admin note), it will not appear to client"))

    def clean(self):
        if self.is_paid and not self.paid_at:
            raise ValidationError("You should specify paid_at Date and Time, if you checked is_paid field")
        if not self.is_paid and self.paid_at:
            raise ValidationError("You should mark is_paid as checked, if you set paid_at Date and Time")
        if self.reward_type == self.BOUNTY and self.bounty == 0:
            raise ValidationError("Reward Bounty should be contains some value $$")


    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_reward_type_display()} - {self.get_criteria_display()}"

    def report_name(self):
        return self.report.title
    report_name.short_description = _("Report Name")

    def report_sequence_id(self):
        return self.report.sequence_id
    report_sequence_id.short_description = _("Report Sequence ID")

    @staticmethod
    def get_earned_rank_level_selector(points) -> str:
        level = ""
        ranking_mechanisms = settings.RANKING_MECHANISM
        for key, val in ranking_mechanisms.items():
            if val["min"] <= points <= val["max"]:
                level = key
        return level

    @staticmethod
    def get_earned_rank_level(user) -> str:
        points = ProgramReportReward.objects.filter(user=user)\
            .aggregate(points=Coalesce(Sum("points"), V(0)))
        return ProgramReportReward.get_earned_rank_level_selector(points=points["points"])

    @staticmethod
    def get_earned_rank_position(user) -> int:
        # GET RANK POSITION BY POINTS
        position = -1
        positions = ProgramReportReward.objects.values("user").annotate(position=Sum("points")).order_by("points")
            #.filter(reward_type=Program.POINTS)\
        """
        OUTPUT:
        <ProgramReportRewardQuerySet [{'user': 2, 'position': 0}, {'user': 10, 'position': 0}]>
        """
        records = list(map(lambda a: a["position"], positions))
        records = list(set(list(records))).sort(reverse=True)
        selected_records = list(filter(lambda a: a["user"] == user.id, positions))

        if records and selected_records:
            position = selected_records[0]["position"]
            position = records.index(position)
        return position