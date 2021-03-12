from django.contrib import admin

from main.core.utils import get_user_search_fields, get_user_class
from ..models import ProgramReport, ProgramPushedReport, ProgramVulnerability


@admin.register(ProgramReport)
class ProgramReportAdmin(admin.ModelAdmin):
    list_display = (
    "title", "document_state", "status", "category", "severity", "vulnerability", "pushed_report", "program",
    "researcher", "guid", "sequence_id", "modified", "created",)
    list_filter = ("status", "category", "severity", "vulnerability", "created", "modified")
    search_fields = ("title", "sequence_id", "guid",) + get_user_search_fields(field_name="researcher")
    date_hierarchy = "created"
    readonly_fields = ("category",)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        User = get_user_class()
        context["adminform"].form.fields['researcher'].queryset = User.objects.filter(role=User.RESEARCHER)
        return super(ProgramReportAdmin, self).render_change_form(request, context, add, change, form_url, obj)


@admin.register(ProgramPushedReport)
class ProgramPushedReportAdmin(admin.ModelAdmin):
    list_display = ProgramReportAdmin.list_display
    list_filter = ProgramReportAdmin.list_filter
    search_fields = ProgramReportAdmin.search_fields
    date_hierarchy = ProgramReportAdmin.date_hierarchy
    readonly_fields = ProgramReportAdmin.readonly_fields

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        User = get_user_class()
        context["adminform"].form.fields['researcher'].queryset = User.objects.filter(role=User.RESEARCHER)
        return super(ProgramPushedReportAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def get_queryset(self, request):
        return super(ProgramPushedReportAdmin, self).get_queryset(request=request).pushed_reports()



@admin.register(ProgramVulnerability)
class ProgramVulnerabilityAdmin(admin.ModelAdmin):
    list_display = ("name", "created")
    search_fields = ("name",)
    date_hierarchy = "created"
