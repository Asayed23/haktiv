from django.utils.translation import gettext_lazy as _
from django.db import models
from django.conf import settings

from main.core.models import UniqueIdentityModel
from main.users.models import User
from .program_report import ProgramReport

class ProgramReportActivity(UniqueIdentityModel):
    class Meta:
        verbose_name = _("Program Report Activity")
        verbose_name_plural = _("Program Report Activities")
        ordering = ("-created",)

    ORDER_BY_DEFAULT = "created"

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DUPLICATED = "duplicated"
    STATUSES = (
        (PENDING, _("Pending"),),
        (APPROVED, _("Approved"),),
        (REJECTED, _("Rejected"),),
        (DUPLICATED, _("Duplicated"),),
    )
    REPORT_IS_SUBMITTED = "report_is_submitted"
    CHANGE_REPORT_STATUS = "change_report_status"
    CHANGE_REPORT_SEVERITY = "change_report_severity"
    PUSH_REPORT_TO_CUSTOMER = "push_report_to_customer"
    TRIAGER_APPLIED_A_CHANGE = "triager_applied_a_change"
    ADD_COMMENT = "add_comment"
    RESEARCHER_CLOSE_REPORT = "researcher_close_report"
    CUSTOMER_CHANGE_STATUS = "customer_change_status"
    COMBINATION = "combination"
    TRIAGED_REWARD_REPORT_BOUNTY = "triaged_reward_bounty"
    TRIAGED_REWARD_REPORT_SWAG = "triaged_reward_swag"
    TRIAGED_REWARD_REPORT_POINTS = "triaged_reward_points"

    ACTIVITY_TYPES = (
        (REPORT_IS_SUBMITTED, _("Report Is Submitted"),),
        (CHANGE_REPORT_STATUS, _("Change Report Status"),),
        (CHANGE_REPORT_SEVERITY, _("Change Report Severity"),),
        (PUSH_REPORT_TO_CUSTOMER, _("Push Report to Customer"),),
        (TRIAGER_APPLIED_A_CHANGE, _("Triager Applied a Change"),),
        (ADD_COMMENT, _("Add Comment"),),
        (RESEARCHER_CLOSE_REPORT, _("Researcher Close Report"),),
        (CUSTOMER_CHANGE_STATUS, _("Customer Change Status"),),
        (COMBINATION, _("Combination"),),
        (TRIAGED_REWARD_REPORT_BOUNTY, _("Triager triaged Reward action on the researcher's report (Bounty Program)"),),
        (TRIAGED_REWARD_REPORT_SWAG, _("Triager triaged Reward action on the researcher's report (SWAG Program)"),),
        (TRIAGED_REWARD_REPORT_POINTS, _("Triager triaged Reward action on the researcher's report (Points Program)"),),
    )

    activity_type = models.CharField(_("Activity Type"), max_length=24, choices=ACTIVITY_TYPES, default=ADD_COMMENT)
    report = models.ForeignKey(ProgramReport, verbose_name=_("Program Report"), on_delete=models.CASCADE)
    status = models.CharField(_("Status"), max_length=24, choices=STATUSES, null=True, blank=True, default=None)
    comment = models.TextField(_("Comment"), max_length=2000,)
    is_closed = models.BooleanField(_("Is Closed"), default=False, help_text=_("Researcher closed the report"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Publisher"), on_delete=models.CASCADE)
    activity = models.TextField(_("Activity Template"), default="", blank=True, max_length=2000)

    def __str__(self):
        return f"{self.report.title} - {self.get_status_display()}"

    @property
    def activity_template(self):
        return self.activity if self.activity else self.set_activity_template()

    def activity_stream(self):
        # This Activity stream custom-computed template activity for dashboard
        template = None
        program = self.report.program.title
        report = self.report.title
        report_status = self.report.status
        if self.activity_type == self.CHANGE_REPORT_STATUS:
            if self.user.role == User.TRIAGER and report_status == ProgramReport.IN_REVIEW:
                template = _("Opened %(report)s on %(program)s") % dict(program=program, report=report)
            elif self.user.role == User.TRIAGER and report_status in [ProgramReport.DUPLICATED, ProgramReport.NA,
                                                                      ProgramReport.INFORMATIVE, ProgramReport.RESOLVED, ]:
                template = _("Closed %(report)s on %(program)s") % dict(program=program, report=report)
        return template or self.activity

    def set_activity_template(self, cost=0.0) -> str:
        # This Activity Template for reports on screen
        template = None
        user = self.user.username
        program = self.report.program.title
        report = self.report.title
        report_status = self.report.status
        report_severity = self.report.severity
        if self.activity_type == self.REPORT_IS_SUBMITTED and self.user.role in [User.RESEARCHER, User.TRIAGER]:
            template = _("%(user)s submitted a report to %(program)s") % dict(user=user, program=program)
        elif self.activity_type == self.CHANGE_REPORT_STATUS:
            template = _("%(user)s changed status to %(report_status)s") % dict(user=user, report_status=report_status)
        elif self.activity_type == self.PUSH_REPORT_TO_CUSTOMER:
            template = _("%(user)s pushed a report to %(program)s") % dict(user=user, program=program)
        elif self.activity_type == self.CHANGE_REPORT_SEVERITY:
            template = _("%(user)s changed report's severity to %(report_severity)s") % dict(user=user, report_severity=report_severity)
        elif self.activity_type == self.ADD_COMMENT:
            template = _("%(user)s posted a comment") % dict(user=user)
        elif self.activity_type == self.RESEARCHER_CLOSE_REPORT:
            template = _("%(user)s self-closed a report on %(program)s") % dict(user=user, program=program)
        elif self.activity_type == self.COMBINATION:
            template = _("comment added by user") % dict(user=user)
        elif self.activity_type == self.TRIAGED_REWARD_REPORT_BOUNTY:
            template = _("%(program)s has rewarded you %(cost)s $ for your finding") % dict(program=program, cost=cost)
        elif self.activity_type == self.TRIAGED_REWARD_REPORT_SWAG:
            template = _("%(program)s has rewarded you SWAG for your finding") % dict(program=program)
        elif self.activity_type == self.TRIAGED_REWARD_REPORT_POINTS:
            template = _("%(program)s has rewarded you Points for your finding") % dict(program=program)
        return str(template) if template else None

    # def activity_template(self, field_name=""):
    #     template = None
    #     user = self.user.username
    #     program = self.report.program.title
    #     report_status = self.report.status
    #     report_status_display = self.report.get_status_display()
    #     report_severity_display = self.report.get_severity_display()
    #     if self.activity_type == self.REPORT_IS_SUBMITTED and self.user.role in [User.RESEARCHER, User.TRIAGER]:
    #         template = _("%(user)s submitted a report to %(program)s") % dict(user=user, program=program)
    #     elif self.activity_type == self.CHANGE_REPORT_STATUS \
    #             and report_status in [ProgramReport.REJECTED, ProgramReport.DUPLICATED] and \
    #             self.user.role in [User.RESEARCHER, User.TRIAGER]:
    #         template = _("%(user)s closed report & changed status to %(report_status_display)s") % dict(
    #             user=user, report_status_display=report_status_display,
    #         )
    #     elif self.activity_type == self.CHANGE_REPORT_STATUS and report_status == ProgramReport.PENDING and \
    #             self.user.role in [User.RESEARCHER, User.TRIAGER]:
    #         template = _("%(user)s changed status to %(report_status_display)s") % dict(
    #             user=user, report_status_display=report_status_display
    #         )
    #     elif self.activity_type == self.CHANGE_REPORT_STATUS and report_status == ProgramReport.APPROVED and \
    #             self.user.role in [User.RESEARCHER, User.TRIAGER]:
    #         template = _("%(user)s changed status to %(report_status_display)s") % dict(
    #             user=user, report_status_display=report_status_display,
    #         )
    #     elif self.activity_type == self.CHANGE_REPORT_SEVERITY:
    #         template = _("%(user)s changed severity to %(report_severity_display)s") % dict(
    #             user=user, report_status_display=report_severity_display,
    #         )
    #     elif self.activity_type == self.PUSH_REPORT_TO_CUSTOMER and self.user.role in [User.CUSTOMER, User.TRIAGER]:
    #         template = _("%(user)s triaged a report to %(program)s") % dict(user=user, program=program,)
    #     elif self.activity_type == self.TRIAGER_APPLIED_A_CHANGE and self.user.role in [User.RESEARCHER, User.TRIAGER]:
    #         template = _("%(user)s applied a change to %(field_name)s") % dict(user=user, field_name=field_name,)
    #     elif self.activity_type == self.ADD_COMMENT:
    #         template = _("%(user)s posted a comment") % dict(user=user)
    #     elif self.activity_type == self.RESEARCHER_CLOSE_REPORT and self.user.role in [User.RESEARCHER, User.TRIAGER]:
    #         template = _("%(user)s closed the report") % dict(user=user)
    #     elif self.activity_type == self.CUSTOMER_CHANGE_STATUS and report_status == ProgramReport.RESOLVED:
    #         if self.user.role in [User.CUSTOMER, User.TRIAGER]:
    #             template = _("%(user)s closed the report & changed status to %(report_status_display)s") % dict(
    #                 user=user, report_status_display=report_status_display,
    #             )
    #         elif self.user.role in [User.RESEARCHER, User.TRIAGER]:
    #             template = _("%(program)s closed the report & changed status to %(report_status_display)s") % dict(
    #                 program=program, report_status_display=report_status_display,
    #             )
    #     elif self.activity_type == self.COMBINATION:
    #         template = _("comment added by %(user)s") % dict(user=user)
    #     return str(template) if template else None
