from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from main.core.utils import get_user_class
from .program import FileManagerShortSerializer
from ...models import ProgramReport, ProgramVulnerability, Program, ProgramReportActivity, ProgramScope


class ProgramReportListSerializer(serializers.Serializer):
    """DOCUMENT_STATES, SEVERITIES, VISIBILITIES, STATUSES, CATEGORIES"""
    document_state = serializers.ChoiceField(choices=ProgramReport.DOCUMENT_STATES, allow_blank=True, required=False)
    severity = serializers.ChoiceField(choices=ProgramReport.SEVERITIES, allow_blank=True, required=False)
    visibility = serializers.ChoiceField(choices=ProgramReport.VISIBILITIES, allow_blank=True, required=False)
    status = serializers.ChoiceField(choices=ProgramReport.STATUSES, allow_blank=True, required=False)
    category = serializers.ChoiceField(choices=ProgramReport.CATEGORIES, allow_blank=True, required=False)
    search = serializers.CharField(label=_("Search"), allow_blank=True, required=False)
    order_by = serializers.ChoiceField(choices=ProgramReport.ORDER_BY, default=ProgramReport.ORDER_BY_DEFAULT,
                                       allow_blank=True, required=False)


class ProgramVulnerabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramVulnerability
        fields = ("name", "guid",)
        lookup_field = "guid"
        extra_kwargs = {
            "url": {"lookup_field": "guid"}
        }


class ProgramReportEmptySerializer(serializers.Serializer):
    pass


class ProgramVulnerabilityListSerializer(serializers.Serializer):
    search = serializers.CharField(label=_("Search"), allow_blank=True, required=False)


class ResearcherSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_class()
        fields = ("first_name", "last_name", "username",)

class TriagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_class()
        fields = ("first_name", "last_name", "username",)


class ProgramForProgramReportSerializer(serializers.ModelSerializer):
    logo = FileManagerShortSerializer(read_only=True, many=False)

    class Meta:
        model = Program
        fields = ("title", "guid", "slug", "status", "visibility", "reward_type", "logo")


class ProgramScopeCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramScope
        fields = ("in_scope_asset", "scope_type", "guid",)


class ProgramReportActivityCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramReportActivity
        exclude = ("id", "user", "report", "created", "modified", "guid",)


class ProgramReportSerializerBase(serializers.ModelSerializer):
    sequence_id = serializers.CharField(allow_blank=True, required=False)
    asset = serializers.CharField(allow_blank=True, required=False)
    vulnerability = ProgramVulnerabilitySerializer(read_only=True, many=False)
    program = ProgramForProgramReportSerializer(read_only=True, many=False)
    researcher = ResearcherSerializer(read_only=True, many=False)
    triager = TriagerSerializer(read_only=True, many=False)
    urls = serializers.ListSerializer(child=serializers.URLField(), allow_empty=False)
    program_scopes = ProgramScopeCustomSerializer(read_only=True, many=True)
    activity_counts = serializers.ReadOnlyField()
    activity_last = ProgramReportActivityCustomSerializer(read_only=True, many=False)
    customer_report = serializers.ReadOnlyField()

    class Meta:
        model = ProgramReport
        fields = (
            "guid", "sequence_id", "asset", "urls", "document_state", "program_scopes", "title", "status", "severity",
            "visibility", "category", "program", "researcher", "triager", "vulnerability", "description", "impact",
            "recommendation", "created", "triaged_at", "is_rewarded", "submitted_at", "activity_counts", "activity_last", "customer_report",)
    # TODO: `created` will be removed
class ProgramReportSerializer(ProgramReportSerializerBase):
    pass


class AllProgramReportSerializer(ProgramReportSerializerBase):
    pass


class PushedProgramReportSerializer(ProgramReportSerializerBase):
    class Meta:
        model = ProgramReport
        fields = (
            "guid", "sequence_id", "asset", "urls", "document_state", "program_scopes", "title", "status", "severity",
            "visibility", "category", "program", "triager", "vulnerability", "description", "impact", "recommendation",
            "created", "triaged_at", "is_rewarded", "submitted_at", "activity_counts", "activity_last", "customer_report",)
