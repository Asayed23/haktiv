import string

from django.conf import settings
from django.db import models
from django.db.models import Max, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
# from django.contrib.postgres.fields import ArrayField

from main.core.models import UniqueIdentityModel
from main.core.utils import password_generator
from .program import Program
from .program_scope import ProgramScope


class ProgramVulnerability(UniqueIdentityModel):
    class Meta:
        verbose_name = _("Program Vulnerability")
        verbose_name_plural = _("Program Vulnerabilities")
        ordering = ("name",)

    name = models.CharField(_("Vulnerability Name"), max_length=100, unique=True)

    def __str__(self):
        return f"{self.name}"

class ProgramReportManager(models.Manager):
    pass


class ProgramReportQuerySet(models.QuerySet):
    def non_pushed_reports(self):
        # THIS REPORTS FOR TRIAGER AND RESEARCHER ONLY
        return self.filter(pushed_report__isnull=True)
    def pushed_reports(self):
        # THIS REPORTS FOR CUSTOMER ONLY
        return self.filter(pushed_report__isnull=False)

    def reports_in_12_month(self):
        today = timezone.datetime.now()
        before12month = today.replace(year=today.year - 1) + timezone.timedelta(days=1)
        return self.non_pushed_reports().filter(created__range=[before12month, today])

class ProgramReport(UniqueIdentityModel):
    class Meta:
        verbose_name = _("Program Report")
        verbose_name_plural = _("Program Reports")
        ordering = ("-modified",)

    DRAFT = "draft"
    PUBLISHED = "published"
    DOCUMENT_STATES = (
        (DRAFT, _("Draft")),
        (PUBLISHED, _("Published")),
    )

    # OTHER = "other"
    # MAJOR = "major"
    # MINOR = "minor"
    # TRIVIAL = "trivial"
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
    SEVERITIES = (
        (CRITICAL, _("Critical")),
        (HIGH, _("High")),
        (MEDIUM, _("Medium")),
        (LOW, _("Low")),
        (INFO, _("Info")),
    )

    PUBLIC = "public"
    PRIVATE = "private"
    VISIBILITIES = (
        (PUBLIC, _("Public"),),
        (PRIVATE, _("Private"),),
    )
    IN_REVIEW = "in-review"
    INFORMATIVE = "informative"
    TRIAGED = "triaged"
    NEED_MORE_INFO = "need-more-info"
    NEW = "new"
    NA = "na"
    DUPLICATED = "duplicated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    SELF_CLOSED = "self-closed"
    STATUSES = (
        (IN_REVIEW, _("In-Review")),
        (INFORMATIVE, _("Informative")),
        (TRIAGED, _("Triaged")),
        (NEED_MORE_INFO, _("Need More Information")),
        (NEW, _("New")),
        (NA, _("N/A")),
        (DUPLICATED, _("Duplicated")),
        (RESOLVED, _("Resolved")),
        (SELF_CLOSED, _("Self-Closed")),
    )
    PENDING = "pending"
    OPEN = "open"
    APPROVED = "approved"
    REJECTED = "rejected"
    CATEGORIES = (
        (PENDING, _("Pending")),
        (OPEN, _("Open")),
        (APPROVED, _("Approved")),
        (REJECTED, _("Rejected")),
        (DUPLICATED, _("Duplicated")),
        (CLOSED, _("Closed")),
    )
    objects = ProgramReportManager.from_queryset(ProgramReportQuerySet)()

    sequence_id = models.CharField(_("Sequence ID"), max_length=200, )
    title = models.CharField(_("Title"), max_length=255)
    document_state = models.CharField(_("Document State"), max_length=24, choices=DOCUMENT_STATES, default=DRAFT)
    asset = models.CharField(_("Asset"), max_length=200, null=True, blank=True)
    program_scopes = models.ManyToManyField(ProgramScope, verbose_name=_("Program Scopes"), blank=True)
    visibility = models.CharField(_("Visibility"), max_length=24, choices=VISIBILITIES, default=PUBLIC)
    status = models.CharField(_("Status"), max_length=24, choices=STATUSES, default=NEW)
    category = models.CharField(_("Category"), max_length=24, choices=CATEGORIES, default=NEW)
    severity = models.CharField(_("Severity"), max_length=24, choices=SEVERITIES, default=None, blank=True, null=True)
    vulnerability = models.ForeignKey(ProgramVulnerability, verbose_name=_("Vulnerability"), on_delete=models.SET_NULL,
                                      blank=True, null=True)
    urls =models.URLField(_("URL"), max_length=200, null=True, blank=True)
    # urls = ArrayField(
    #     models.URLField(_("URL"), max_length=200, null=True, blank=True), size=20,
    # )
    program = models.ForeignKey(Program, verbose_name=_("Program"), on_delete=models.CASCADE)
    description = models.TextField(_("Description"), help_text=_("Markdown Text"))
    impact = models.TextField(_("Impact"), max_length=2000, help_text=_("Markdown Text"))
    recommendation = models.TextField(_("Recommendation"), help_text=_("Markdown Text"))
    researcher = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Submitted by (Researcher)"),
                                   on_delete=models.CASCADE, related_name='program_report_researcher')
    triager = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Approved by (Triager)"),
                                on_delete=models.SET_NULL, blank=True, null=True, related_name='program_report_triager')
    triaged_at = models.DateTimeField(_("Triaged At"), blank=True, null=True)
    # THE PARENT REPORT REFERENCE HERE
    pushed_report = models.OneToOneField('self', verbose_name=_("Pushed Report"),
                                         on_delete=models.SET_NULL, blank=True, null=True)

    # def update_category2(self):
    #     if self.status == self.IN_REVIEW:
    #         self.category = self.PENDING
    #     elif self.status == self.INFORMATIVE:
    #         self.category = self.REJECTED
    #     elif self.status == self.TRIAGED:
    #         self.category = self.APPROVED
    #     elif self.status == self.NEED_MORE_INFO:
    #         self.category = self.PENDING
    #     elif self.status == self.NEW:
    #         self.category = self.OPEN
    #     elif self.status == self.NA:
    #         self.category = self.REJECTED
    #     elif self.status == self.DUPLICATED:
    #         self.category = self.DUPLICATED
    #     elif self.status == self.RESOLVED:
    #         self.category = self.APPROVED
    #     elif self.status == self.CLOSED:
    #         self.category = self.CLOSED

    def update_category(self):
        if self.status == self.NEW:
            self.category = self.PENDING
        elif self.status in [self.IN_REVIEW, self.TRIAGED, self.NEED_MORE_INFO]:
            self.category = self.OPEN
        elif self.status in [self.INFORMATIVE, self.NA, self.DUPLICATED, self.RESOLVED, self.SELF_CLOSED]:
            self.category = self.CLOSED
        if self.status == self.TRIAGED and not self.triaged_at:
            self.triaged_at = timezone.now()

    def is_locked(self):
        return self.category == self.CLOSED

    @property
    def submitted_at(self):
        # Get First Submitted Report Date Time
        return self.pushed_report.created if self.pushed_report else self.created

    @property
    def is_rewarded(self):
        # find is this report is rewarded in report or in customer version report also.
        from .program_report_reward import ProgramReportReward
        return ProgramReportReward.objects.filter(
            user=self.researcher
        ).filter(Q(report=self)|Q(report=self.pushed_report)).exists()

    def customer_report(self):
        # find source report
        report = ProgramReport.objects.filter(pushed_report__guid=self.guid).first()
        return report.guid if report else None

    @property
    def is_pushed_report(self):
        return True if self.customer_report() else False

    def __str__(self):
        return f"{self.title} {self.sequence_id}"

    def get_next_id(self):
        default_start = 143
        id_max = ProgramReport.objects.aggregate(Max('id'))["id__max"]
        return id_max + default_start if id_max else default_start

    def comments(self):
        from .program_report_activity import ProgramReportActivity
        return ProgramReportActivity.objects.filter(report=self)

    def activity_counts(self):
        return self.comments().count()

    def activity_last(self):
        return self.comments().last()



class ProgramPushedReport(ProgramReport):
    class Meta:
        proxy = True
        verbose_name = _("Program Pushed Report")
        verbose_name_plural = _("Program Pushed Reports")
