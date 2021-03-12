from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Sum, Value as V, Count
from django.db.models.functions import Coalesce

from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from main.core.api_base import APIResponseBase
from main.core.utils import paginate
from main.users.backends import IsTriager, IsResearcher
from main.users.models import User, UserTraffic
from ..serializers import ResearcherDashboardEmptySerializer, TriagerDashboardEmptySerializer, \
    ProgramReportActivityDashboardSerializer, FileManagerDashboardSerializer, UserDashboardSerializer, \
    TriagerDashboardSerializer
from ...models import ProgramReportActivity, ProgramReportReward, ProgramReport, Program, get_past_month_range


class DashboardBase(GenericViewSet, APIResponseBase):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = ProgramReportActivity.objects.all()
    serializer_class = ProgramReportActivityDashboardSerializer
    http_method_names = ['get']  # 'get', 'post', 'head', 'put', 'patch'
    lookup_field = "username"

    def get_user(self):
        return User.objects.filter(username=self.kwargs.get("username")).first()

class ResearcherDashboardView(DashboardBase):
    """
    Any User has authenticated
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProgramReportActivity.objects.filter(
            user__username=self.kwargs.get("username"),
            #report__status__in=[ProgramReport.SELF_CLOSED, ProgramReport.NEW],
            activity_type__in=[ProgramReportActivity.REPORT_IS_SUBMITTED,
                        ProgramReportActivity.RESEARCHER_CLOSE_REPORT],
        ).order_by("-created")
        #.exclude(
        #     activity__exact='',
        #     activity__isnull=True,
        #     activity_type__in=[ProgramReportActivity.PUSH_REPORT_TO_CUSTOMER]
        # )

    @swagger_auto_schema(query_serializer=ResearcherDashboardEmptySerializer)
    @action(detail=False)
    def dashboard(self, request, *args, **kwargs):
        user = self.get_user()
        if not user:
            return self.error(code=404, message=_("User does not matched!"))
        user_traffic_created = UserTraffic.register_visit(user=user, visitor=request.user)
        response = {}
        response["user"] = dict(
            full_name=user.get_full_name(),
            username=user.username,
            avatar=UserDashboardSerializer(instance=user, many=False, context={"request": request}).data.get("avatar"),
            socials=list(map(lambda a: dict(
                social=a.social,
                link=a.link,
            ), user.get_social_media())),
            points=ProgramReportReward.objects.filter(user=user)
                .aggregate(points=Coalesce(Sum("points"), V(0)))["points"],
        )
        response["rank"] = dict(
            level=ProgramReportReward.get_earned_rank_level(user=user),
            position=ProgramReportReward.get_earned_rank_position(user=user),
        )
        response["fame"] = dict(
            views=UserTraffic.get_visit_count(user=user),
            last_view=UserTraffic.get_visit_latest(user=user),
        )
        program_pks = ProgramReport.objects.filter(researcher=user).values_list("program", flat=True)
        programs = Program.objects.filter(visibility=Program.PUBLIC, pk__in=program_pks).order_by("-modified")
        response["program"] = list(map(lambda a: {
            "slug": a.slug,
            "logo": FileManagerDashboardSerializer(instance=a.logo, many=False, context={"request": request}).data.get("src")
        }, programs[:8]))
        # response["report"] = ProgramReport.objects.filter(researcher=user)\
        #     .values("status").annotate(num=Count("status")).order_by("-num")
        response["report"] = dict(
            submitted=ProgramReport.objects.filter(researcher=user).non_pushed_reports().count(),
            rewarded=ProgramReportReward.objects.filter(user=user).count(),
            pending=ProgramReport.objects.filter(researcher=user, status=ProgramReport.NEW).non_pushed_reports().count(),
        )
        report_types = ProgramReport.objects.filter(researcher=user).non_pushed_reports()\
            .values("program_scopes__scope_type")\
            .annotate(num=Count("program_scopes")).order_by("-num")
        report_types = list(map(lambda a: dict(
            type=a["program_scopes__scope_type"],
            num=a["num"],
        ), report_types))
        response["report_types"] = list(filter(lambda a: a.get("type") != None, report_types))
        return self.success(code=200, data=response)

    @swagger_auto_schema(query_serializer=ResearcherDashboardEmptySerializer)
    @action(detail=False, serializer_class=ProgramReportActivityDashboardSerializer)
    def stream(self, request, *args, **kwargs):
        response = {}
        queryset = self.get_queryset()
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=request.query_params.get("per_page", 10),
                            page=request.query_params.get("page"))
        serializer = self.get_serializer(queryset, many=True)
        response["record_counts"] = record_counts
        response["queryset"] = serializer.data
        return self.success(code=200, data=response)


class TriagerDashboardView(DashboardBase):
    """
    Only Triager level allowed
    """
    permission_classes = [IsAuthenticated, IsTriager]

    def get_queryset(self):
        return ProgramReportActivity.objects.filter(
            user__username=self.kwargs.get("username"),
            activity_type__in=[ProgramReportActivity.CHANGE_REPORT_STATUS],
            report__status__in=[ProgramReport.IN_REVIEW, ProgramReport.DUPLICATED, ProgramReport.NA,
                            ProgramReport.INFORMATIVE, ProgramReport.RESOLVED],
        ).order_by("-created")
        # .exclude(activity__exact='', activity__isnull=True)

    def get_closed_reports(self):
        return ProgramReport.objects.reports_in_12_month().filter(
            triager__username=self.kwargs.get("username"),
            status__in=[ProgramReport.DUPLICATED, ProgramReport.NA, ProgramReport.INFORMATIVE, ProgramReport.RESOLVED]
        )

    @swagger_auto_schema(query_serializer=TriagerDashboardSerializer)
    @action(detail=False, serializer_class=TriagerDashboardEmptySerializer)
    def dashboard(self, request, *args, **kwargs):
        user = self.get_user()
        if user and user.role != User.TRIAGER:
            return self.error(code=403, message=_("This user does not have triager role"))
        response = {}
        response["total_closed_reports"] = self.get_closed_reports()\
            .values("status")\
            .annotate(num=Count("status")).order_by("-num")

        program_pks = ProgramReport.objects.filter(triager=user).values_list("program", flat=True)
        program_pks = list(set(program_pks))
        programs = Program.objects.filter(visibility=Program.PUBLIC, pk__in=program_pks).order_by("-modified")
        response["program"] = list(map(lambda a: {
            "slug": a.slug,
            "logo": FileManagerDashboardSerializer(instance=a.logo, many=False, context={"request": request}).data.get(
                "src")
        }, programs[:8]))
        reports = ProgramReport.objects
        report_date_range = request.data.get("report_date_range")
        if report_date_range == "this-month":
            reports = reports.filter(created__month=timezone.now().month)
        elif report_date_range == "prev-month":
            reports = reports.filter(created__range=[get_past_month_range()])
        opened = reports.filter(triager=user, status=ProgramReport.IN_REVIEW).count()
        closed = reports.filter(triager=user, status__in=[
            ProgramReport.DUPLICATED, ProgramReport.NA, ProgramReport.INFORMATIVE, ProgramReport.RESOLVED
        ]).count()
        pending = reports.filter(triager=user, status=ProgramReport.NEW).count()
        response["report"] = dict(
            opened=opened,
            closed=closed,
            pending=pending,
            total=opened+closed+pending,
        )
        report_types = ProgramReport.objects.filter(triager=user) \
            .values("program_scopes__scope_type") \
            .annotate(num=Count("program_scopes")).order_by("-num")
        report_types = list(map(lambda a: dict(
            type=a["program_scopes__scope_type"],
            num=a["num"],
        ), report_types))
        response["report_types"] = list(filter(lambda a: a.get("type") != None, report_types))
        return self.success(code=200, data=response)

    @swagger_auto_schema(query_serializer=TriagerDashboardEmptySerializer)
    @action(detail=False, serializer_class=ProgramReportActivityDashboardSerializer)
    def stream(self, request, *args, **kwargs):
        response = {}
        queryset = self.get_queryset()
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=request.query_params.get("per_page", 10),
                            page=request.query_params.get("page"))
        serializer = self.get_serializer(queryset, many=True)
        response["record_counts"] = record_counts
        response["queryset"] = serializer.data
        return self.success(code=200, data=response)
