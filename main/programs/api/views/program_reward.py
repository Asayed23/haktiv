from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from main.core.api_base import APIResponseBase
from main.core.utils import paginate, get_query
from main.users.models import User

from ..serializers import ProgramRewardSerializer
from ...models import ProgramReward

class ProgramRewardView(ModelViewSet, APIResponseBase):
    permission_classes = [IsAuthenticated]
    serializer_class = ProgramRewardSerializer
    lookup_field = "slug"
    http_method_names = ['get',] # 'post', 'head', 'put', 'patch'

    def get_queryset(self):
        return ProgramReward.objects.filter(program__slug=self.kwargs["program_slug"])

    @swagger_auto_schema(responses={status.HTTP_200_OK: ProgramRewardSerializer})
    def list(self, request, program_guid=None, guid=None, *args, **kwargs):
        page = request.query_params.get("page")
        per_page = request.query_params.get("per_page", 10)
        queryset = self.get_queryset()
        record_counts = queryset.count()
        queryset = paginate(queryset, per_page=per_page, page=page)
        serializer_class = ProgramRewardSerializer
        serializer = serializer_class(queryset, many=True)
        return self.success(code=200, data=dict(record_counts=record_counts, queryset=serializer.data))

    def create(self, request, *args, **kwargs):
        if request.user.role != User.TRIAGER:
            return self.error(code=401, message=_("This user's role not allowed to submit reward"))
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
