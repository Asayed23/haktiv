from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from main.filemanager.models import FileManager
from main.programs.models import ProgramReportActivity

class ResearcherDashboardEmptySerializer(serializers.Serializer):
    pass
class TriagerDashboardEmptySerializer(serializers.Serializer):
    pass

class TriagerDashboardSerializer(serializers.Serializer):
    report_date_range = serializers.ChoiceField(choices=(
        ("all", _("All")),
        ("this-month", _("This Month")),
        ("prev-month", _("Previous Month")),
    ))

class FileManagerDashboardSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()
    class Meta:
        model = FileManager
        fields = ("src",)
    def get_src(self, obj):
        request = self.context.get('request')
        src = obj.src
        return request.build_absolute_uri(src)

class UserDashboardSerializer(serializers.Serializer):
    avatar = serializers.ImageField(read_only=True)


class ProgramReportActivityDashboardSerializer(serializers.ModelSerializer):
    activity_stream = serializers.ReadOnlyField()
    class Meta:
        model = ProgramReportActivity
        fields = ("created", "activity_stream",)