from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from django.urls import path, re_path
from main.users.api import views

app_name = "api_users"

router = DefaultRouter()
# router.register('profile', UserProfileModelViewSet, basename='user_profile_api')
router.register('social_media', views.UserSocialMediaView)

urlpatterns = [
    re_path(r'^register/researcher/$', views.ResearcherRegistrationView.as_view(), name='researcher_register'),
    re_path(r'^register/company/$', views.CompanyRegistrationView.as_view(), name='company_register'),
    # re_path(r'^verification/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #         UserRegisterAPI.as_view(), name="user_Activation"),

    # 2 Factor Authentication
    re_path(r'^2fa/$', views.TwoFactorView.as_view(), name="2fa_handler"),
    re_path(r'^2fa/qr/$', views.TwoFactorQRCodeView.as_view(), name="2fa_qr_image"),

    # Reset Password
    # re_path(r'^reset/$', UserResetPasswordRequest.as_view(), name='reset_password_request'),
    # re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z_\-]+)/$',
    #         UserResetPasswordConfirm.as_view(), name='reset_password_confirm'),
    # re_path(r'^reset/change-password/$', ChangePassword.as_view(), name='change_password'),
    # path('profile/', views.UserProfileModelViewSet.as_view({'get': 'list'})),
    # path('profile/', views.UserProfileAPIView.as_view()),
    path('profile/', views.UserProfileModelViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}))
] + router.urls