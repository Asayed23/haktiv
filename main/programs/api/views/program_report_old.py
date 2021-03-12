from uuid import uuid4

from django.db.models import Q
from django.utils.translation import ugettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from main.core.api_base import APIResponseBase
from main.core.utils import paginate, get_query
from main.notify.models import Notification
from main.users.models import User
from ..serializers import AllProgramReportSerializer, ProgramReportEmptySerializer, PushedProgramReportSerializer, \
    ProgramReportSerializer, ProgramReportListSerializer
from ...models import ProgramReport, ProgramVulnerability, Program, ProgramScope


class ProgramReportBase(ModelViewSet, APIResponseBase):
    pass


class ProgramReportView(ModelViewSet, APIResponseBase):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ProgramReportSerializer
    lookup_field = "guid"
    http_method_names = ['get', 'post', 'head', 'put', 'patch']

    def get_queryset(self):
        return ProgramReport.objects.filter(program__slug=self.kwargs["program_slug"])

    @swagger_auto_schema(responses={status.HTTP_200_OK: ProgramReportSerializer},
                         query_serializer=ProgramReportListSerializer)
    def list(self, request, program_guid=None, guid=None, *args, **kwargs):
        search = request.query_params.get("search")
        page = request.query_params.get("page")
        per_page = request.query_params.get("per_page", 10)
        order_by = request.query_params.get("order_by")
        document_state = request.query_params.get("document_state")
        severity = request.query_params.get("severity")
        visibility = request.query_params.get("visibility")
        status = request.query_params.get("status")
        category = request.query_params.get("category")
        queryset = self.get_queryset().filter(visibility=ProgramReport.PUBLIC)
        if request.user.role == User.RESEARCHER:
            queryset |= self.get_queryset().filter(researcher=request.user)
        if document_state:
            queryset = queryset.filter(document_state=document_state)
        if severity:
            queryset = queryset.filter(severity=severity)
        if visibility:
            queryset = queryset.filter(visibility=visibility)
        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category=category)
        if search:
            entry_query = get_query(search, ("title", "sequence_id", "guid",))
            queryset = queryset.filter(entry_query)
        if order_by and order_by in ProgramReport.ORDER_BY:
            queryset = queryset.order_by(order_by)
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=per_page, page=page)
        serializer_class = ProgramReportSerializer
        serializer = serializer_class(queryset, many=True)
        return self.success(code=200, data=dict(record_counts=record_counts, queryset=serializer.data))

    def perform_create(self, serializer):
        serializer.save(
            program=serializer.initial_data["program"],
            researcher=serializer.initial_data["researcher"],
            vulnerability=serializer.initial_data.get("vulnerability"),
        )

    def create(self, request, *args, **kwargs):
        data_patched = request.data.copy()
        vulnerability = request.data.get("vulnerability")
        program = Program.objects.filter(slug=self.kwargs["program_slug"]).first()
        program_scopes = ProgramScope.objects.filter(
            guid__in=[program_scope for program_scope in request.data.get("program_scopes", [])], program=program,
            scope_status=ProgramScope.IN_SCOPE)
        if vulnerability:
            vulnerability = ProgramVulnerability.objects.filter(guid=vulnerability).first()
            if vulnerability:
                data_patched.update(dict(vulnerability=vulnerability))
        if program:
            data_patched.update(dict(program=program))
        data_patched.update(dict(researcher=self.request.user))
        serializer = self.get_serializer(data=data_patched)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        for program_scope in program_scopes:
            serializer.instance.program_scopes.add(program_scope)
        headers = self.get_success_headers(serializer.data)
        return self.success(code=status.HTTP_201_CREATED, data=serializer.data, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success(code=200, data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.is_locked():
            return self.error(code=401, message=_("You cannot submit new activity, while report closed"))
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return self.success(code=200, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        return self.error(code=status.HTTP_403_FORBIDDEN, message=_('Delete function is not offered in this path.'))


class AllProgramReportView(GenericViewSet, RetrieveModelMixin, UpdateModelMixin, ListModelMixin, APIResponseBase):
    """
AllProgramReportView:
Allowed roles: CUSTOMER, TRIAGER, ADMIN, note (RESEARCHER NOT ALLOWED)

mixins.CreateModelMixin,
mixins.RetrieveModelMixin,
mixins.UpdateModelMixin,
mixins.DestroyModelMixin,
mixins.ListModelMixin,
GenericViewSet
"""
    permission_classes = [IsAuthenticated, ]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = ProgramReport.objects.all()
    serializer_class = AllProgramReportSerializer
    lookup_field = "guid"
    http_method_names = ['get', 'post', 'head', 'put', 'patch']

    def get_queryset(self):
        queryset = ProgramReport.objects.none()
        if self.request.user.role == User.CUSTOMER:
            queryset |= ProgramReport.objects.filter(program__customer=self.request.user)
        elif self.request.user.role == User.TRIAGER:
            queryset |= ProgramReport.objects.filter(Q(triager=self.request.user) | Q(researcher=self.request.user))
        elif self.request.user.role == User.RESEARCHER:
            queryset |= ProgramReport.objects.filter(researcher=self.request.user)
        elif self.request.user.role == User.ADMIN:
            queryset = ProgramReport.objects.all()
        return queryset

    @swagger_auto_schema(query_serializer=ProgramReportListSerializer)
    def list(self, request, *args, **kwargs):
        search = request.query_params.get("search")
        order_by = request.query_params.get("order_by")
        page = request.query_params.get("page")
        per_page = request.query_params.get("per_page", 10)
        document_state = request.query_params.get("document_state")
        severity = request.query_params.get("severity")
        visibility = request.query_params.get("visibility")
        status = request.query_params.get("status")
        category = request.query_params.get("category")
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.user.role == User.TRIAGER:
            # GET Assigned Reports
            queryset = queryset.filter(triager=self.request.user).exclude(researcher=self.request.user)
        if document_state:
            queryset = queryset.filter(document_state=document_state)
        if severity:
            queryset = queryset.filter(severity=severity)
        if visibility:
            queryset = queryset.filter(visibility=visibility)
        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category=category)
        if search:
            entry_query = get_query(search, ("title", "sequence_id", "guid",))
            queryset = queryset.filter(entry_query)
        if order_by and order_by in ProgramReport.ORDER_BY:
            queryset = queryset.order_by(order_by)
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=per_page, page=page)
        serializer = self.get_serializer(queryset, many=True)
        return self.success(code=200, message=_("OK"), data=dict(record_counts=record_counts, queryset=serializer.data))

    def perform_create(self, serializer):
        serializer.save(
            program=serializer.initial_data["program"],
            researcher=serializer.initial_data["researcher"],
            vulnerability=serializer.initial_data.get("vulnerability"),
        )

    def create(self, request, *args, **kwargs):
        if not self.request.user.role in [User.RESEARCHER, User.TRIAGER]:
            return self.error(code=401, message=_("Role not allowed"))
        data_patched = request.data.copy()
        vulnerability = request.data.get("vulnerability")
        program_guid = request.data.get("program")
        if not program_guid:
            return self.error(code=403, message=_("Program guid required, please specify the program guid"))
        program = Program.objects.filter(guid=program_guid).first()
        program_scopes = ProgramScope.objects.filter(
            guid__in=[program_scope for program_scope in request.data.get("program_scopes", [])], program=program,
            scope_status=ProgramScope.IN_SCOPE)
        if vulnerability:
            ProgramVulnerability.objects.filter(guid=vulnerability).first()
            data_patched.update(dict(vulnerability=vulnerability))
        if program:
            data_patched.update(dict(program=program))
        data_patched.update(dict(researcher=self.request.user))
        serializer = self.get_serializer(data=data_patched)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        for program_scope in program_scopes:
            serializer.instance.program_scopes.add(program_scope)
        headers = self.get_success_headers(serializer.data)
        return self.success(code=status.HTTP_201_CREATED, data=serializer.data, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success(code=200, data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.is_locked():
            return self.error(code=401, message=_("You cannot submit new activity, while report closed"))
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return self.success(code=200, data=serializer.data)

    @action(detail=False, serializer_class=ProgramReportEmptySerializer)
    def document_states(self, request, *args, **kwargs):
        return self.success(code=200, data={k: v for k, v in ProgramReport.DOCUMENT_STATES})

    @action(detail=False, serializer_class=ProgramReportEmptySerializer)
    def severities(self, request, *args, **kwargs):
        return self.success(code=200, data={k: v for k, v in ProgramReport.SEVERITIES})

    @action(detail=False, serializer_class=ProgramReportEmptySerializer)
    def visibilites(self, request, *args, **kwargs):
        return self.success(code=200, data={k: v for k, v in ProgramReport.VISIBILITIES})

    @action(detail=False, serializer_class=ProgramReportEmptySerializer)
    def statuses(self, request, *args, **kwargs):
        return self.success(code=200, data={k: v for k, v in ProgramReport.STATUSES})

    @action(detail=False, serializer_class=ProgramReportEmptySerializer)
    def categories(self, request, *args, **kwargs):
        return self.success(code=200, data={k: v for k, v in ProgramReport.CATEGORIES})

    @swagger_auto_schema(query_serializer=ProgramReportListSerializer)
    @action(detail=False)
    def triager_submitted_reports(self, request, *args, **kwargs):
        # Get Submitted Reports
        if self.request.user.role != User.TRIAGER:
            return self.error(code=401, message=_("Role not allowed"))
        search = request.query_params.get("search")
        order_by = request.query_params.get("order_by")
        page = request.query_params.get("page")
        per_page = request.query_params.get("per_page", 10)
        queryset = ProgramReport.objects.filter(researcher=self.request.user).exclude(triager=self.request.user)
        queryset = self.filter_queryset(queryset)
        if search:
            entry_query = get_query(search, ("title", "sequence_id", "guid",))
            queryset = queryset.filter(entry_query)
        if order_by and order_by in ProgramReport.ORDER_BY:
            queryset = queryset.order_by(order_by)
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=per_page, page=page)
        serializer = self.get_serializer(queryset, many=True)
        return self.success(code=200, message=_("OK"), data=dict(record_counts=record_counts, queryset=serializer.data))


class PushedProgramReportView(ModelViewSet, APIResponseBase):
    """ This class created for pushed report to customers
Class: ProgramPushedReportView
Allowed roles: CUSTOMER, TRIAGER
"""
    permission_classes = [IsAuthenticated, ]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = ProgramReport.objects.all()
    serializer_class = PushedProgramReportSerializer
    lookup_field = "guid"
    http_method_names = ['get', 'post', 'head', 'put', 'patch', 'delete']

    def get_queryset(self):
        queryset = ProgramReport.objects.none()
        if self.request.user.role == User.CUSTOMER:
            queryset |= ProgramReport.objects.filter(pushed_report__guid=self.kwargs["report_guid"],
                                                     program__customer=self.request.user, pushed_report__isnull=True)
        elif self.request.user.role == User.TRIAGER:
            queryset |= ProgramReport.objects.filter(pushed_report__guid=self.kwargs["report_guid"],
                                                     program__triagers__in=[self.request.user],
                                                     pushed_report__isnull=True)
        return queryset

    @swagger_auto_schema(query_serializer=ProgramReportListSerializer)
    def list(self, request, *args, **kwargs):
        search = request.query_params.get("search")
        order_by = request.query_params.get("order_by")
        page = request.query_params.get("page")
        per_page = request.query_params.get("per_page", 10)
        queryset = self.filter_queryset(self.get_queryset())
        if search:
            entry_query = get_query(search, ("title", "sequence_id", "guid", "program_scope__guid"))
            queryset = queryset.filter(entry_query)
        if order_by and order_by in ProgramReport.ORDER_BY:
            queryset = queryset.order_by(order_by)
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=per_page, page=page)
        serializer = self.get_serializer(queryset, many=True)
        return self.success(code=200, message=_("OK"), data=dict(record_counts=record_counts, queryset=serializer.data))

    def perform_create(self, serializer):
        serializer.save(
            program=serializer.initial_data["program"],
            researcher=serializer.initial_data["researcher"],
            vulnerability=serializer.initial_data.get("vulnerability"),
            pushed_report=serializer.initial_data.get("pushed_report"),
        )

    def create(self, request, *args, **kwargs):
        if request.user.ROLE != User.TRIAGER:
            return self.error(code=status.HTTP_401_UNAUTHORIZED, message=_("This method not allowed for this role"))
        source_report = ProgramReport.objects.filter(guid=self.kwargs["report_guid"],
                                                     pushed_report__is_null=True).first()
        if not source_report:
            return self.error(code=status.HTTP_400_BAD_REQUEST, message=_("You cannot create pushed program report"))
        data_patched = request.data.copy()
        data_patched.update(dict(
            program=source_report.program,
            researcher=source_report.researcher,
            vulnerability=source_report.vulnerability,
            pushed_report=source_report,
        ))
        serializer = self.get_serializer(data=data_patched)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return self.success(code=status.HTTP_201_CREATED, data=serializer.data, headers=headers)

    def create1(self, request, *args, **kwargs):
        if request.user.ROLE != User.TRIAGER:
            return self.error(code=status.HTTP_401_UNAUTHORIZED, message=_("This method not allowed for this role"))
        obj = ProgramReport.objects.filter(guid=self.kwargs["report_guid"], pushed_report__is_null=True).first()
        if not obj:
            return self.error(code=status.HTTP_400_BAD_REQUEST, message=_("You cannot create pushed program report"))
        # pushed_report = obj
        # pushed_report.pk = None
        # pushed_report.guid = uuid4()
        # pushed_report.save()
        # obj.pushed_report = pushed_report
        # obj.save()
        obj.id = None
        obj.guid = uuid4()
        obj.pushed_reports = ProgramReport.objects.filter(guid=self.kwargs["report_guid"],
                                                          pushed_report__is_null=True).first()
        obj.save()
        Notification.notify_user(
            title=_("New Report Pushed"),
            body=f"New report triaged to customer by {self.request.user.get_short_name()}",
            category=Notification.REPORT,
            user=obj.program.customer,
        )
        return self.success(code=status.HTTP_201_CREATED,
                            data=dict(pushed_report=obj.pushed_reports.guid, report=obj.guid))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success(code=200, data=serializer.data)

    def update(self, request, *args, **kwargs):
        if request.user.ROLE != User.TRIAGER:
            return self.error(code=status.HTTP_401_UNAUTHORIZED, message=_("This method not allowed for this role"))
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.is_locked():
            return self.error(code=401, message=_("You cannot submit new activity, while report closed"))
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return self.success(code=200, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        if request.user.ROLE != User.TRIAGER:
            return self.error(code=status.HTTP_401_UNAUTHORIZED, message=_("This method not allowed for this role"))
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.success(status=status.HTTP_204_NO_CONTENT, message=_("OK"))
