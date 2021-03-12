from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from main.core.api_base import APIResponseBase
from main.core.utils import paginate, get_query
from main.users.models import User
from ..serializers import ProgramReportRewardSerializer, ProgramReportRewardListSerializer
from ...models import ProgramReport, ProgramReportReward, ProgramReward, ProgramReportActivity, Program


class ProgramReportRewardView(ModelViewSet, APIResponseBase):
    permission_classes = [IsAuthenticated]
    serializer_class = ProgramReportRewardSerializer
    lookup_field = "guid"
    http_method_names = ['get', 'post',]  # 'post', 'head', 'put', 'patch'

    def get_queryset(self):
        return ProgramReportReward.objects.filter(report__guid=self.kwargs["report_guid"])

    @swagger_auto_schema(responses={status.HTTP_200_OK: ProgramReportRewardListSerializer})
    def list(self, request, report_guid=None, guid=None, *args, **kwargs):
        page = request.query_params.get("page")
        per_page = request.query_params.get("per_page", 10)
        queryset = self.get_queryset()
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=per_page, page=page)
        serializer_class = ProgramReportRewardSerializer
        serializer = serializer_class(queryset, many=True)
        return self.success(code=200, data=dict(record_counts=record_counts, queryset=serializer.data))

    def perform_create(self, serializer):
        serializer.save(
            report=serializer.initial_data["report"],
            user=serializer.initial_data.get("user"),
        )

    def create(self, request, *args, **kwargs):
        data_patched = request.data.copy()
        report = ProgramReport.objects.filter(guid=self.kwargs["report_guid"]).first()
        program_reward = ProgramReward.objects.filter(program=report.program, criteria=report.severity).first()
        if not report:
            return self.error(code=400, message=_("No Program Report matched"))
        if report.program.reward_type == Program.BOUNTY and not program_reward:
            return self.error(code=400, message=_("No Program Reward matched"))
        if request.user.role != User.TRIAGER:
            return self.error(code=status.HTTP_401_UNAUTHORIZED, message=_("This method not allowed for this role"))
        if report.triager != request.user:
            return self.error(code=status.HTTP_401_UNAUTHORIZED, message=_("You cannot reward program report, you are not the triager of this report"))
        if report.is_rewarded:
            return self.error(code=400, message=_("This report already rewarded"))
        if not report.is_pushed_report:
            # IF NOT PUSHED TO CUSTOMER -> THEN NOT REWARD
            return self.error(code=400, message=_("You cannot reward program report, Report Not Pushed yet!"))
        if program_reward:
            # CALCULATE THE REWARD as [BOUNTY] TO RESEARCHER
            swag = program_reward.swag
            points = program_reward.get_earned_points()
            bounty = program_reward.bounty
        else:
            # CALCULATE THE REWARD as [SWAG, POINTS] TO RESEARCHER
            swag = ""
            points = ProgramReward.get_earned_points_variant(
                    criteria=report.severity,
                    reward_type=report.program.reward_type,
                )
            bounty = 0.0
        data_patched.update(dict(
            criteria=report.severity,
            reward_type=report.program.reward_type,
            report=report,
            swag=swag,
            points=points,
            bounty=bounty,
            user=report.researcher,
        ))
        comment = request.data.get("comment")
        if comment:
            if report.program.reward_type == Program.BOUNTY:
                activity_type = ProgramReportActivity.TRIAGED_REWARD_REPORT_BOUNTY
            elif report.program.reward_type == Program.SWAG:
                activity_type = ProgramReportActivity.TRIAGED_REWARD_REPORT_SWAG
            else:
                activity_type = ProgramReportActivity.TRIAGED_REWARD_REPORT_POINTS

            obj = ProgramReportActivity.objects.create(
                activity_type=activity_type,
                report=report,
                status=ProgramReportActivity.APPROVED,
                comment=comment,
                is_closed=True,
                user=report.researcher,
                activity="",
            )
            obj.activity = obj.set_activity_template(cost=bounty)
            obj.save()
        serializer = self.get_serializer(data=data_patched)
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