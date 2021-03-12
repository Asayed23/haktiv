from django.contrib import admin
from django.contrib import messages
from django.utils import timezone

from main.core.utils import get_user_class, get_user_search_fields
from ..models import Program, ProgramReward


def close_program(modeladmin, request, queryset):
    for obj in queryset:
        program = obj
        program.status = Program.INACTIVE
        program.end_date = timezone.now()
        program.save()
        # send email to triagers
    messages.success(request, "Selected Programs has been closed")
close_program.short_description = "Close Program"

class ProgramStackedInline(admin.StackedInline):
    model = ProgramReward
    extra = 0
    fields  = ("criteria", "bounty", "points",)
    readonly_fields = ("points",)
    exclude = ("swag",)
    #max_num = 10

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    inlines = [ProgramStackedInline]
    list_display = ("title", "logo", "customer", "guid", "sequence_id", "modified", "created",)
    list_filter = ("status", "visibility", "tags", "reward_type",)
    search_fields = get_user_search_fields("customer") + ("guid", "sequence_id", "title",)
    date_hierarchy = "created"
    add_form_template = 'admin/program_add.html'
    change_form_template = 'admin/program_add.html'

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        User = get_user_class()
        context["adminform"].form.fields['customer'].queryset = User.objects.filter(role=User.CUSTOMER)
        context["adminform"].form.fields['triagers'].queryset = User.objects.filter(role=User.TRIAGER)
        context["adminform"].form.fields['hackers'].queryset = User.objects.filter(role=User.RESEARCHER)
        return super(ProgramAdmin, self).render_change_form(request, context, add, change, form_url, obj)