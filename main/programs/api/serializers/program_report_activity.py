from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from main.core.utils import get_user_class
from ...models import ProgramReportActivity

class ProgramReportActivityUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_class()
        fields = ("first_name", "last_name", "avatar",)

class ProgramReportActivitySerializer(serializers.ModelSerializer):
    user = ProgramReportActivityUserSerializer(read_only=True, many=False)
    is_edited = serializers.ReadOnlyField()
    activity_template = serializers.ReadOnlyField()
    class Meta:
        model = ProgramReportActivity
        # fields = "__all__"
        exclude = ("id", "report",)

class ProgramReportActivityListSerializer(serializers.Serializer):
    search = serializers.CharField(label=_("Search"), allow_blank=True, required=False)
    order_by = serializers.ChoiceField(choices=ProgramReportActivity.ORDER_BY,
                                       default=ProgramReportActivity.ORDER_BY_DEFAULT,
                                       allow_blank=True, required=False)

class ProgramReportActivityEmptySerializer(serializers.Serializer):
    pass
