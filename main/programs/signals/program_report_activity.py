from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _

from main.notify.models import Notification
from main.programs.models import ProgramReportActivity
from main.users.models import User


@receiver(pre_save, sender=ProgramReportActivity)
def set_activity_template_before_program_report_activity(sender, instance, **kwargs):
    if not instance.activity:
        # if activity_template set default computed field before save
        instance.activity = instance.set_activity_template()