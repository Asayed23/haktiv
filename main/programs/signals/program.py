import string

from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _

from main.core.utils import password_generator
from main.notify.models import Notification
from main.programs.models import Program


@receiver(pre_save, sender=Program)
def generate_program_sequence_id(sender, instance, **kwargs):
    if not instance.pk:
        instance.sequence_id = f"{password_generator(size=2, chars=string.ascii_uppercase)}{str(instance.get_next_id()).zfill(5)}"


@receiver(post_save, sender=Program)
def save_program(sender, instance, created, **kwargs):
    users = [*instance.triagers.all(), *instance.hackers.all()]
    if created:
        for user in users:
            Notification.notify_user(
                title=_("New Program"),
                body=f"New Program added to HAKTIV: {instance.title}",
                category=Notification.PROGRAM,
                user=user,
            )
    else:
        for user in users:
            Notification.notify_user(
                title=_("Program Updated"),
                body=f"Program has been updated: {instance.title}",
                category=Notification.PROGRAM,
                user=user,
            )


@receiver(pre_delete, sender=Program)
def delete_program(sender, instance, **kwargs):
    users = [*instance.triagers.all(), *instance.hackers.all()]
    for user in users:
        Notification.notify_user(
            title=_("Program Deleted"),
            body=f"Program has been deleted: {instance.title}",
            category=Notification.PROGRAM,
            user=user,
        )
