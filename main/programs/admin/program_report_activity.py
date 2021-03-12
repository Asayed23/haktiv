from django.contrib import admin

from main.core.utils import get_user_search_fields, get_user_class
from ..models import ProgramReportActivity


@admin.register(ProgramReportActivity)
class ProgramReportActivityAdmin(admin.ModelAdmin):
    list_display = ("report", "status", "activity_type", "is_closed", "user", "created")
    list_filter = ("status", "is_closed", "activity_type")
    search_fields = ("report__title",) + get_user_search_fields(field_name="user")

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        User = get_user_class()
        context["adminform"].form.fields['user'].queryset = User.objects.filter(role__in=[User.RESEARCHER, User.TRIAGER])
        return super(ProgramReportActivityAdmin, self).render_change_form(request, context, add, change, form_url, obj)
