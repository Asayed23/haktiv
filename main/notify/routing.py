# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import path
from main.notify.consumers import NotfiyConsumer

websocket_urlpatterns = [
    path('ws/notify/', NotfiyConsumer.as_asgi(), name="notify_user_ws"),
]