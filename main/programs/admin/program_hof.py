from django.contrib import admin

from main.core.utils import get_user_search_fields
from ..models import ProgramHallOfFame

@admin.register(ProgramHallOfFame)
class ProgramHOF(admin.ModelAdmin):
    list_display = ("program", "hacker", "is_top")
    list_filter = ("is_top",)
    search_fields = ("program__title",) + get_user_search_fields(field_name="hacker")
    date_hierarchy = "created"
