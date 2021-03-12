from django.utils.translation import ugettext as _
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.viewsets import ModelViewSet

from main.core.api_base import APIResponseBase
from ...models import User, UserSocialMedia
from ..serializers import UserSocialMediaSerializer


class UserSocialMediaView(ModelViewSet, APIResponseBase):
    permission_classes = [IsAuthenticated, ]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = UserSocialMedia.objects.all()
    serializer_class = UserSocialMediaSerializer
    lookup_field = "guid"
    http_method_names = ['get', 'post', 'head', 'put', 'patch', 'delete']