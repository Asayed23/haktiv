from rest_framework import serializers

from main.users.models import User
from ...models import ProgramReportReward, ProgramReport, Program, ProgramReward


class ProgramReportRewardUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username",)


class ProgramReportIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramReport
        fields = ("title", "guid",)

class ProgramReportRewardListSerializer(serializers.Serializer):
    criteria = serializers.ChoiceField(choices=ProgramReward.CRITERIA_CHOICES, allow_blank=True, required=False)
    reward_type = serializers.ChoiceField(choices=Program.REWARD_TYPES, allow_blank=True, required=False)

class ProgramReportRewardSerializer(serializers.ModelSerializer):
    user = ProgramReportRewardUserSerializer(many=False, read_only=True)
    report = ProgramReportIDSerializer(many=False, read_only=True)

    class Meta:
        model = ProgramReportReward
        fields = ("criteria", "reward_type", "swag", "points", "bounty", "report", "user",)
