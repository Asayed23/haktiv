from django.db.models import Q
from django.utils.translation import ugettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from main.core.api_base import APIResponseBase
from main.core.utils import paginate, get_query
from main.users.models import User
from ..serializers import ProgramSerializer, ProgramListSerializer, ProgramTypeTagSerializer, ProgramHackerSerializer, \
    ProgramStatisticsSerializer, ProgramLogoSerializer, ProgramEmptySerializer, ProgramHallOfFameSerializer
from ...models import Program, ProgramTypeTag, ProgramScope


class ProgramBase(ModelViewSet, APIResponseBase):
    permission_classes = [IsAuthenticated, ]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    lookup_field = "slug"
    http_method_names = ['get', 'post', 'head', 'put', 'patch']

    def program_list_filter(self, request, queryset):
        program_type_tags = request.query_params.get("program_type_tags")
        reward_type = request.query_params.get("reward_type")
        status = request.query_params.get("status")
        visibility = request.query_params.get("visibility")
        search = request.query_params.get("search")
        order_by = request.query_params.get("order_by")
        if program_type_tags:
            queryset = queryset.filter(tags__name__in=program_type_tags)
        if reward_type:
            queryset = queryset.filter(reward_type=reward_type)
        if status:
            queryset = queryset.filter(status=status)
        if visibility:
            queryset = queryset.filter(visibility=visibility)
        if search:
            entry_query = get_query(search, ("title", "guid", "sequence_id",))
            queryset = queryset.filter(entry_query)
        if order_by and order_by in Program.ORDER_BY:
            queryset = queryset.order_by(order_by)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return self.success(code=status.HTTP_201_CREATED, data=serializer.data, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success(code=200, data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.customer != request.user:
            return self.error(code=400, message=_("Permission denied, user not allowed to modify the program"))
        ### HANDLING ProgramScope in Program ###
        scopes = request.data.get("scopes")
        scopes_guids = []
        for scope in scopes:
            if isinstance(scope, dict):
                if any([param not in scope for param in ("scope_type", "scope_status", "in_scope_asset",)]):
                    return self.error(code=400, message=_("missing required parameter in program_scope"))
                if "guid" in scope:
                    # UPDATE (Program Scope)
                    guid = scope.get("guid")
                    program_scope = ProgramScope.objects.filter(guid=guid).first()
                    if program_scope:
                        program_scope.scope_type = scope.get("scope_type")
                        program_scope.scope_status = scope.get("scope_status")
                        program_scope.in_scope_asset = scope.get("in_scope_asset")
                        program_scope.save()
                else:
                    # CREATE (Program Scope)
                    program_scope = ProgramScope.objects.create(
                        program=instance,
                        scope_type=scope.get("scope_type"),
                        scope_status=scope.get("scope_status"),
                        in_scope_asset=scope.get("in_scope_asset"),
                    )
                if program_scope:
                    scopes_guids.append(program_scope.guid)
        # DELETE (Program Scope)
        for program_scope in ProgramScope.objects.filter(program=instance).exclude(guid__in=scopes_guids):
            program_scope.delete()
        ### HANDLING ProgramScope in Program ###
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


class ProgramView(ProgramBase):

    def get_queryset(self):
        queryset = Program.objects.none()
        if self.request.user.role == User.CUSTOMER:
            queryset = Program.objects.filter(customer=self.request.user)
        elif self.request.user.role == User.TRIAGER:
            queryset = Program.objects.filter(visibility=Program.PUBLIC).exclude(triagers__in=[self.request.user])
        elif self.request.user.role == User.RESEARCHER:
            queryset = Program.objects.filter(
                Q(hackers__in=[self.request.user], visibility=Program.PRIVATE) | Q(visibility=Program.PUBLIC))
        elif self.request.user.role == User.ADMIN:
            queryset = Program.objects.all()
        return queryset

    @swagger_auto_schema(query_serializer=ProgramListSerializer)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = self.program_list_filter(request=request, queryset=queryset)
        queryset = queryset.distinct()
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=request.query_params.get("per_page", 10),
                            page=request.query_params.get("page"))
        serializer = self.get_serializer(queryset, many=True)
        return self.success(code=200, message=_("OK"), data=dict(record_counts=record_counts, queryset=serializer.data))

    @swagger_auto_schema(serializer_class=ProgramLogoSerializer,
                         responses={status.HTTP_201_CREATED: ProgramLogoSerializer})
    @action(methods=['post'], detail=True, parser_classes=[MultiPartParser, FormParser],
            serializer_class=ProgramLogoSerializer)
    def logo_save(self, request, format=None, *args, **kwargs):
        program = self.get_object()
        if program.customer != request.user:
            return self.error(code=400, message=_("Permission denied, you are not allowed to change the logo"))
        serializer = ProgramLogoSerializer(data=request.data, instance=program.logo)
        if serializer.is_valid():
            program.logo = serializer.save()
            program.logo.source = request.FILES["source"]
            program.save()
            return self.success(code=201, message=_("Logo has submitted successfully"))
        return self.error(code=400, )

    @swagger_auto_schema(responses={status.HTTP_200_OK: None})
    @action(detail=True, methods=["post"], parser_classes=[FormParser], serializer_class=ProgramEmptySerializer)
    def logo_remove(self, request, format=None, *args, **kwargs):
        program = self.get_object()
        if program.customer != request.user:
            return self.error(code=400, message=_("Permission denied, you are not allowed to change the logo"))
        if program.logo:
            program.logo.delete()
            program.logo = None
            program.save()
            return self.success(code=200, message=_("Logo has been delete successfully"))
        return self.error(code=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(serializer_class=ProgramHackerSerializer,
                         responses={status.HTTP_200_OK: ProgramHackerSerializer})
    @action(detail=True, serializer_class=ProgramHackerSerializer)
    def hackers(self, request, *args, **kwargs):
        program = self.get_object()
        page = request.query_params.get("page")
        per_page = request.query_params.get("per_page", 10)
        queryset = program.hackers.all()
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=per_page, page=page)
        serializer_class = ProgramHackerSerializer
        serializer = serializer_class(queryset, many=True)
        return self.success(code=200, data=dict(record_counts=record_counts, queryset=serializer.data))

    @swagger_auto_schema(serializer_class=ProgramHallOfFameSerializer,
                         responses={status.HTTP_200_OK: ProgramHallOfFameSerializer})
    @action(detail=True, serializer_class=ProgramHallOfFameSerializer)
    def hall_of_fame(self, request, *args, **kwargs):
        program = self.get_object()
        page = request.query_params.get("page")
        per_page = request.query_params.get("per_page", 10)
        queryset = program.hall_of_fame()
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=per_page, page=page)
        serializer_class = ProgramHallOfFameSerializer
        serializer = serializer_class(queryset, many=True)
        return self.success(code=200, data=dict(record_counts=record_counts, queryset=serializer.data))

    @swagger_auto_schema(serializer_class=ProgramStatisticsSerializer,
                         responses={status.HTTP_200_OK: ProgramStatisticsSerializer})
    @action(detail=True, serializer_class=ProgramEmptySerializer)
    def statistics(self, request, *args, **kwargs):
        program = self.get_object()
        return self.success(code=200, data=program.get_statistics())


class ProgramTriagerView(ProgramBase):
    permission_classes = [IsAuthenticated, ]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    lookup_field = "slug"
    http_method_names = ['get', 'post', 'head', 'put', 'patch']

    def get_queryset(self):
        queryset = Program.objects.none()
        if self.request.user.role == User.TRIAGER:
            queryset = Program.objects.filter(triagers__in=[self.request.user])
        return queryset

    @swagger_auto_schema(query_serializer=ProgramListSerializer)
    def list(self, request, *args, **kwargs):
        # Get Submitted Programs
        if self.request.user.role != User.TRIAGER:
            return self.error(code=401, message=_("Role not allowed"))
        queryset = self.filter_queryset(self.get_queryset())
        queryset = self.program_list_filter(request=request, queryset=queryset)
        queryset = queryset.distinct()
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=request.query_params.get("per_page", 10),
                            page=request.query_params.get("page"))
        serializer = self.get_serializer(queryset, many=True)
        return self.success(code=200, message=_("OK"), data=dict(record_counts=record_counts, queryset=serializer.data))


class ProgramTypeTagView(ModelViewSet, APIResponseBase):
    permission_classes = [AllowAny]
    queryset = ProgramTypeTag.objects.all()
    serializer_class = ProgramTypeTagSerializer
    lookup_field = "guid"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return self.success(code=200, data=serializer.data)
