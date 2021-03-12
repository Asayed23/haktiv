from django.db.models.signals import pre_save, post_save
from django.db.models import Min, Count
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _

from main.notify.models import Notification
from main.programs.models import ProgramReport, ProgramReportActivity
from main.users.models import User


@receiver(pre_save, sender=ProgramReport)
def generate_program_report_sequence_id(sender, instance, **kwargs):
    if not instance.pk:
        if not instance.pushed_report:
            instance.sequence_id = f"HAK{str(instance.get_next_id()).zfill(5)}"
        if not instance.triager:
            ## The Old Design: Assign Triager To Report from Program Triagers Automatically
            # triager = User.objects.filter(pk__in=instance.program.triagers.values_list("id", flat=True))\
            #    .exclude(pk=instance.researcher.pk).order_by("?").first()
            ## Change Request: ASSIGN TRIAGER TO REPORT FROM PROGRAM EQUALLY NOT RANDOMLY
            triager = None
            triagers = User.objects.filter(pk__in=instance.program.triagers.values_list("id", flat=True))\
                .exclude(pk=instance.researcher.pk)
            '''
            ## According to Change Request:
            x = ProgramReport.objects.filter(program__slug="western-digital-program",
                                             program__triagers__pk__in=triagers)\
                .values("triager").annotate(report=Count("triager")).order_by("triager")
            <ProgramReportQuerySet [{'triager': 4, 'report': 15}, {'triager': 9, 'report': 18}, 
                                    {'triager': 10, 'report': 45}, {'triager': None, 'report': 0}]>
            '''

            all_reports = ProgramReport.objects.filter(
                program=instance.program,
                program__triagers__pk__in=triagers).values("triager")\
                .annotate(report=Count("triager")).order_by("triager")

            report_count = -1
            for record in all_reports:
                if record["report"] < report_count:
                    report_count = record["report"]
                    triager = User.objects.filter(pk=record["triager"]).first()
            if not triager:
                triager = User.objects.filter(
                    pk__in=instance.program.triagers.values_list("id", flat=True)
                ).exclude(pk=instance.researcher.pk).order_by("?").first()
            if triager:
                instance.triager = triager
        # Notify Users
        for user in [instance.researcher, instance.triager, instance.program.customer]:
            if user:
                Notification.notify_user(
                    title=_("New Report has been submitted"),
                    body=f"New Program Report {instance.title}",
                    category=Notification.REPORT,
                    user=user,
                )
    else:
        for user in [instance.researcher, instance.triager, instance.program.customer]:
            if user:
                Notification.notify_user(
                    title=_("Program Report has been modified"),
                    body=f"Program Report {instance.title}",
                    category=Notification.REPORT,
                    user=user,
                )


@receiver(pre_save, sender=ProgramReport)
def set_program_report_update_category(sender, instance, **kwargs):
    instance.update_category()

@receiver(post_save, sender=ProgramReport)
def submit_activity_to_program_report(sender, instance, created, **kwargs):
    if created:
        if instance.researcher and not instance.pushed_report and \
                instance.researcher.role in [User.RESEARCHER, User.TRIAGER]:
            ProgramReportActivity.objects.create(
                activity_type=ProgramReportActivity.REPORT_IS_SUBMITTED,
                report=instance,
                comment="",
                user=instance.researcher,
            )
        elif instance.triager and instance.triager.role == User.TRIAGER and instance.pushed_report:
            # This is Push Report to Customer Activity
            ProgramReportActivity.objects.create(
                activity_type=ProgramReportActivity.PUSH_REPORT_TO_CUSTOMER,
                report=instance,
                comment="",
                user=instance.triager,
            )