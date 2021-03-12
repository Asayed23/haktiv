from django.contrib import admin

from main.core.utils import get_user_search_fields, get_user_class
from ..models import ProgramReportReward


@admin.register(ProgramReportReward)
class ProgramReportRewardAdmin(admin.ModelAdmin):
    list_display = ("criteria", "reward_type", "bounty", "report_name", "report_sequence_id", "user", "is_paid", "paid_at", "created",)
    list_filter = ("criteria", "reward_type", "is_paid", "paid_at",)
    search_fields = get_user_search_fields("user") + ("report__title",)
    date_hierarchy = "created"
    readonly_fields = ("swag", "points",)
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        User = get_user_class()
        context["adminform"].form.fields['user'].queryset = User.objects.filter(
            role__in=[User.TRIAGER, User.RESEARCHER])
        return super(ProgramReportRewardAdmin, self).render_change_form(request, context, add, change, form_url, obj)
