from django.db.models.signals import post_save
from django.dispatch import receiver

from main.notify.models import Notification
from main.users.models import User


@receiver(post_save, sender=User)
def save_user(sender, instance, created, **kwargs):
    if created:
        Notification.notify_user(title="Welcome to Haktiv",
                                 body="Congratulation, welcome on the HAKTIV board",
                                 category=Notification.GENERAL,
                                 user=instance,
                                 )
    else:
        Notification.notify_user(title="Profile Update",
                                 body="Your profile has been update successfully",
                                 category=Notification.GENERAL,
                                 user=instance,
                                 )
