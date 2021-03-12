from django.contrib import admin

from ..models import ProgramReward


@admin.register(ProgramReward)
class ProgramRewardAdmin(admin.ModelAdmin):
    list_display = ("swag", "points", "bounty", "program",)
    search_fields = ("program__title",)