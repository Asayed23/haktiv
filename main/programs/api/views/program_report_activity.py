from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin, DestroyModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_yasg.utils import swagger_auto_schema

from main.core.api_base import APIResponseBase
from main.core.utils import paginate, get_query
from main.users.models import User
from main.notify.models import Notification
from ...models import ProgramReportActivity, ProgramReport
from ..serializers import ProgramReportActivitySerializer, ProgramReportActivityListSerializer, \
    ProgramReportActivityEmptySerializer

class ProgramReportActivityView(ModelViewSet, APIResponseBase):
    permission_classes = [IsAuthenticated, ]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = ProgramReportActivity.objects.none()
    serializer_class = ProgramReportActivitySerializer
    lookup_field = "guid"
    http_method_names = ['get', 'post', 'head',] # 'put', 'patch', 'delete'

    def get_queryset(self):
        report = ProgramReport.objects.filter(guid=self.kwargs["report_guid"]).first()
        queryset = ProgramReportActivity.objects.filter(report=report)
        if report and report.pushed_report:
            queryset = queryset.exclude(status__in=[ProgramReportActivity.REPORT_IS_SUBMITTED,
                                                ProgramReportActivity.RESEARCHER_CLOSE_REPORT])
        return queryset

    @swagger_auto_schema(query_serializer=ProgramReportActivityListSerializer)
    def list(self, request, *args, **kwargs):
        search = request.query_params.get("search")
        order_by = request.query_params.get("order_by")
        page = request.query_params.get("page")
        per_page = request.query_params.get("per_page", 10)
        queryset = self.filter_queryset(self.get_queryset())
        if search:
            entry_query = get_query(search, ("comment",))
            queryset = queryset.filter(entry_query)
        if order_by and order_by in ProgramReportActivity.ORDER_BY:
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by(ProgramReportActivity.ORDER_BY_DEFAULT)
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=per_page, page=page)
        serializer = self.get_serializer(queryset, many=True)
        return self.success(code=200, message=_("OK"), data=dict(record_counts=record_counts, queryset=serializer.data))

    def perform_create(self, serializer):
        serializer.save(
            report=ProgramReport.objects.filter(guid=self.kwargs["report_guid"]).first(),
            user=self.request.user,
        )

    def create(self, request, *args, **kwargs):
        report = ProgramReport.objects.filter(guid=self.kwargs["report_guid"]).first()
        if report.is_locked():
            return self.error(code=401, message=_("You cannot submit new activity, while report closed"))
        user = report.triager if report.researcher == request.user else report.researcher
        if user: # TO AVOID violates not-null constraint
            Notification.notify_user(
                title="New Comment added to report",
                body=f"New Comment added by {request.user.get_short_name()}",
                category=Notification.REPORT,
                user=user,
                from_user=request.user,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return self.success(data=serializer.data, code=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(query_serializer=ProgramReportActivitySerializer)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success(code=200, data=serializer.data)

    @swagger_auto_schema(query_serializer=ProgramReportActivitySerializer)
    def update(self, request, *args, **kwargs):
        report = ProgramReport.objects.filter(guid=self.kwargs["report_guid"]).first()
        if report.is_locked():
            return self.error(code=401, message=_("You cannot submit new activity, while report closed"))
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance.user == request.user:
            self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return self.success(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user == request.user:
            self.perform_destroy(instance)
            return self.success(code=status.HTTP_204_NO_CONTENT)
        else:
            return self.error(code=401, message=_("Permission Denied"))

    @action(detail=False, serializer_class=ProgramReportActivityEmptySerializer)
    def statuses(self, request, *args, **kwargs):
        return self.success(code=200, data={k: v for k, v in ProgramReportActivity.STATUSES})