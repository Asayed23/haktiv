from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ...models import ProgramReportReward


class EarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramReportReward
        fields = ("criteria", "reward_type", "swag", "points", "bounty", "report", "user",)


class EarningEmptySerializer(serializers.Serializer):
    pass


class EarningListSerializer(serializers.Serializer):
    scope = serializers.ChoiceField(label=_("Scope"), choices=ProgramReportReward.AVAILABLE_SCOPES,
                                    default=ProgramReportReward.DEFAULT_SCOPE, allow_blank=True, required=False)
    search = serializers.CharField(label=_("Search"), allow_blank=True, required=False)
    order_by = serializers.ChoiceField(choices=ProgramReportReward.SPECIAL_ORDER_BY,
                                       default=ProgramReportReward.ORDER_BY_DEFAULT,
                                       allow_blank=True, required=False)
