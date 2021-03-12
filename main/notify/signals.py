# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from main.notify.models import Notification
from main.notify.livecast import send_to_notfiy_ws

@receiver(post_save, sender=Notification)
def create_notifications(instance, created, **kwargs):
    """
        [Hook For new Notifications]
    """
    if created:
        pass
        # send_to_notfiy_ws(user=instance.user, **kwargs)
# post_save.connect(create_notifications, sender=Notification)
