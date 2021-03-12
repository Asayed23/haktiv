from django.utils.translation import gettext_lazy as _
from django.apps import apps
from rest_framework import serializers

from main.core.utils import get_user_class
from main.filemanager.models import FileManager
from ...models import Program, ProgramTypeTag, ProgramReward, ProgramScope, ProgramHallOfFame


class FileManagerShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileManager
        fields = ("source", "url", "storage",)


class ProgramTypeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramTypeTag
        exclude = tuple()


class ProgramGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ("guid", "slug", "title",)


class ProgramRewardSerializer(serializers.ModelSerializer):
    program = ProgramGuideSerializer(read_only=True)

    class Meta:
        model = ProgramReward
        exclude = ("id", "created", "modified", "swag", "points",)
        lookup_field = "guid"
        extra_kwargs = {
            "url": {"lookup_field": "guid"}
        }

class ProgramReward4ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramReward
        fields = ("criteria", "bounty",)


class ProgramScopeSerializer(serializers.ModelSerializer):
    program = ProgramGuideSerializer(read_only=True)
    in_scope_asset = serializers.CharField(allow_blank=False, required=True)

    class Meta:
        model = ProgramScope
        exclude = ("id", "created", "modified",)
        lookup_field = "guid"
        extra_kwargs = {
            "url": {"lookup_field": "guid"}
        }


class ProgramScopeListSerializer(serializers.Serializer):
    scope_status = serializers.ChoiceField(choices=ProgramScope.SCOPE_STATUSES, allow_blank=True, required=False)
    scope_type = serializers.ChoiceField(choices=ProgramScope.SCOPE_TYPES, allow_blank=True, required=False)


def get_program_type_tags():
    from django.db import connection
    if connection.introspection.table_names():
        # program_type_tag_model = apps.get_model('programs', 'ProgramTypeTag')
        # return program_type_tag_model.objects.values_list('name', flat=True)
        return []
    else:
        return []


class ProgramListSerializer(serializers.Serializer):
    program_type_tags = serializers.MultipleChoiceField(choices=get_program_type_tags(), allow_blank=True,
                                                        required=False)
    reward_type = serializers.ChoiceField(choices=Program.REWARD_TYPES, allow_blank=True, required=False)
    status = serializers.ChoiceField(choices=Program.STATUSES, allow_blank=True, required=False)
    visibility = serializers.ChoiceField(choices=Program.VISIBILITIES, allow_blank=True, required=False)
    search = serializers.CharField(label=_("Search"), allow_blank=True, required=False)


class ProgramSerializer(serializers.ModelSerializer):
    tags = ProgramTypeTagSerializer(read_only=True, many=True)
    rewards = ProgramReward4ProgramSerializer(source="program_reward_program", read_only=True, many=True)
    scopes = ProgramScopeSerializer(source="program_scope_program", read_only=True, many=True)
    sequence_id = serializers.CharField(allow_blank=True, required=False)
    submitted_reports = serializers.ReadOnlyField()
    rewarded_reports = serializers.ReadOnlyField()
    paid_bounties = serializers.ReadOnlyField()
    logo = FileManagerShortSerializer(read_only=True, many=False)

    class Meta:
        model = Program
        exclude = ("id", "created", "modified", "triagers", "hackers",)
        lookup_field = "guid"
        extra_kwargs = {
            "url": {"lookup_field": "guid"}
        }


class ProgramEmptySerializer(serializers.Serializer):
    pass


class ProgramHackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_class()
        fields = ("first_name", "last_name", "username", "email", "phone")


class ProgramHallOfFameSerializer(serializers.ModelSerializer):
    program = ProgramGuideSerializer(read_only=True, many=False)
    hacker = ProgramHackerSerializer(read_only=True, many=False)

    class Meta:
        model = ProgramHallOfFame
        fields = ("program", "hacker")


class ProgramStatisticsSerializer(serializers.Serializer):
    submitted_reports = serializers.IntegerField(default=0)
    accepted_reports = serializers.IntegerField(default=0)
    rewarded_reports = serializers.IntegerField(default=0)
    last_submitted_date = serializers.DateTimeField()
    paid_bounties = serializers.FloatField(default=0.0)
    days_since_report_solved = serializers.IntegerField(default=0)


class ProgramLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileManager
        fields = ["source"]

    def save(self, *args, **kwargs):
        if self.instance and self.instance.source:
            self.instance.source.delete()
        return super(ProgramLogoSerializer, self).save(*args, **kwargs)
