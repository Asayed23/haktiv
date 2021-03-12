from django.contrib import admin

from ..models import ProgramScope


@admin.register(ProgramScope)
class ProgramScopeAdmin(admin.ModelAdmin):
    list_display = ("program", "scope_type", "scope_status",)
    list_filter = ("scope_type", "scope_status",)
    search_fields = ("program__title",)
    date_hierarchy = "created"
