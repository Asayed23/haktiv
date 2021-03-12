from django.db.models import Sum, Value as V
from django.db.models.functions import Coalesce
from django.db.models.functions import TruncDay, TruncMonth, ExtractMonth
from django.utils import timezone
from django.utils.translation import ugettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from main.core.api_base import APIResponseBase
from main.core.utils import paginate, get_query
from ..serializers import EarningEmptySerializer, EarningListSerializer
from ...models import ProgramReportReward, Program


class EarningView(APIResponseBase, GenericViewSet):
    permission_classes = [IsAuthenticated, ]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = ProgramReportReward.objects.all()
    serializer_class = EarningEmptySerializer
    http_method_names = ['get']  # 'get', 'post', 'head', 'put', 'patch'

    # INDICATOR field
    INCREASED = "increased"
    DECREASED = "decreased"
    NEUTRAL = "neutral"

    def queryset_list_filter(self, request, queryset):
        scope = request.query_params.get("scope")
        search = request.query_params.get("search")
        order_by = request.query_params.get("order_by")
        if scope == ProgramReportReward.UPCOMING:
            queryset = queryset.upcoming_payments()
        elif scope == ProgramReportReward.PAST_MONTH:
            queryset = queryset.past_month_payments()
        elif scope == ProgramReportReward.COMPLETED:
            queryset = queryset.completed_payments()
        if search:
            entry_query = get_query(search, (
                "report__title", "report__sequence_id", "report__program__title", "guid",))
            queryset = queryset.filter(entry_query)
        if order_by and order_by in ProgramReportReward.SPECIAL_ORDER_BY:
            queryset = queryset.order_by(ProgramReportReward.SPECIAL_ORDER_BY[order_by])
        return queryset

    def get_queryset(self):
        return ProgramReportReward.objects.filter(user=self.request.user, reward_type=Program.BOUNTY)

    @swagger_auto_schema(query_serializer=EarningListSerializer)
    @action(detail=False, serializer_class=EarningEmptySerializer)
    def earnings(self, request, *args, **kwargs):
        response = {}
        queryset = self.get_queryset()
        # Upcoming Payments
        upcoming = queryset.upcoming_payments() \
            .aggregate(upcoming=Coalesce(Sum("bounty"), V(0)))
        # Past Month
        past_month = queryset.past_month_payments() \
            .aggregate(past_month=Coalesce(Sum("bounty"), V(0)))
        # completed Payments
        completed = queryset.completed_payments() \
            .aggregate(completed=Coalesce(Sum("bounty"), V(0)))
        # Increased / Decreased Worth
        second_past_month = queryset.second_past_month_payments() \
            .aggregate(second_past_month=Coalesce(Sum("bounty"), V(0)))
        second_past_month = second_past_month["second_past_month"]
        past_month = past_month["past_month"]
        # INDICATOR must be: INCREASED, DECREASED, or NEUTRAL
        if second_past_month < past_month:
            indicator = self.INCREASED
        elif second_past_month > past_month:
            indicator = self.DECREASED
        else:
            indicator = self.NEUTRAL
        response["indicator"] = indicator
        response["upcoming"] = upcoming["upcoming"]
        response["past_month"] = past_month
        response["completed"] = completed["completed"]
        queryset = self.queryset_list_filter(request=request, queryset=queryset)
        response["record_counts"] = queryset.count()
        queryset = paginate(queryset, per_page=request.query_params.get("per_page", 10),
                            page=request.query_params.get("page"))

        def get_program(program):
            return {
                "title": program.title,
                "slug": program.slug,
                "sequence_id": program.sequence_id,
                "logo": program.logo.src,
            }

        def get_report(report):
            return {
                "title": report.title,
                "guid": report.guid,
                "sequence_id": report.sequence_id,
            }

        response["queryset"] = list(map(lambda reward: {
            "program": get_program(program=reward.report.program),
            "report": get_report(report=reward.report),
            "reward": {
                "reward_date": reward.created.isoformat(),
                "estimated_date": reward.created + timezone.timedelta(days=60),
                "paid_date": reward.paid_at,
                "is_paid": reward.is_paid,
                "amount": "$ {:.2f}".format(reward.bounty),
            }
        }, queryset))
        return self.success(code=200, message=_("OK"), data=response)

    @action(detail=False, serializer_class=EarningEmptySerializer)
    def past_month(self, request, *args, **kwargs):
        # TOTAL BOUNTY BY DAYS OF PAST MONTH
        response = {}
        queryset = self.get_queryset().past_month_payments()
        response["values"] = queryset.annotate(day=TruncDay('paid_at')) \
            .values("day") \
            .annotate(bounty=Sum('bounty')) \
            .order_by("-day")
        # response["values"] = list(
        #     map(lambda a: dict(
        #         t=int(time.mktime(a.created.timetuple()) * 1000.0),
        #         y=str(a.bounty)
        #     ), queryset)
        # )
        return self.success(code=200, message=_("OK"), data=response)

    @action(detail=False, serializer_class=EarningEmptySerializer)
    def completed_payments(self, request, *args, **kwargs):
        # TOTAL BOUNTY BY 12 MONTH AGO
        response = {}
        queryset = self.get_queryset().completed_payments_12_month()
        response["values"] = queryset.annotate(month=TruncMonth('paid_at')) \
            .values("month") \
            .annotate(bounty=Sum('bounty')) \
            .order_by("-month")
        # response["values"] = list(
        #     map(lambda a: dict(
        #         t=int(time.mktime(a.created.timetuple()) * 1000.0),
        #         y=str(a.bounty)
        #     ), queryset)
        # )
        return self.success(code=200, message=_("OK"), data=response)
