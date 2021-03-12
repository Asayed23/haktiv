from rest_framework import routers
from django.urls import path, include
from .views import NotificationView

app_name = "api_notify"

router = routers.DefaultRouter()
router.register('', NotificationView, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]