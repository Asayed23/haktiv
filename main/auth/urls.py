from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import HaktivTokenView, TokenTestView

app_name = 'auth'

urlpatterns = [
    path('token/', HaktivTokenView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/test/', TokenTestView.as_view(), name='token_test'),
]

