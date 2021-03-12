from django.utils.translation import ugettext as _
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from main.core.api_base import APIResponseBase
from main.core.utils import paginate
from ..serializers import NotificationSerializer, NotificationEmptySerializer, NotificationListSerializer, \
    NotificationMarkAsReadOrUnreadSerializer
from ...models import Notification


class NotificationView(GenericViewSet, RetrieveModelMixin, UpdateModelMixin, ListModelMixin, APIResponseBase):
    permission_classes = [IsAuthenticated, ]
    serializer_class = NotificationSerializer
    lookup_field = "guid"
    http_method_names = ['get', 'post', 'head']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @swagger_auto_schema(responses={status.HTTP_200_OK:NotificationListSerializer})
    def list(self, request, program_guid=None, guid=None, *args, **kwargs):
        page = request.query_params.get("page")
        per_page = request.query_params.get("per_page", 10)
        queryset = self.get_queryset()
        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=per_page, page=page)
        serializer_class = NotificationSerializer
        serializer = serializer_class(queryset, many=True)
        return self.success(code=200, data=dict(record_counts=record_counts, queryset=serializer.data))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success(code=200, data=serializer.data)

    @action(detail=False, serializer_class=NotificationEmptySerializer)
    def categories(self, request, *args, **kwargs):
        return self.success(code=200, data={k: v for k, v in Notification.CATEGORIES})

    @action(detail=False, serializer_class=NotificationMarkAsReadOrUnreadSerializer)
    def mark_as_read_all(self, request, *args, **kwargs):
        Notification.objects.filter(user=self.request.user).update(read=True)
        return self.success(code=200, message=_("All Notifications are marked as read"), data={})

    @action(detail=True, serializer_class=NotificationMarkAsReadOrUnreadSerializer)
    def mark_as_read(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.success(code=200, message=_("This Notification marked as read"), data=serializer.data)

    @action(detail=True, serializer_class=NotificationMarkAsReadOrUnreadSerializer)
    def mark_as_unread(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.success(code=200, message=_("This Notification marked as unread"), data=serializer.data)
