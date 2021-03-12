from django.contrib import admin

from ..models import UserTraffic


@admin.register(UserTraffic)
class UserTrafficAdmin(admin.ModelAdmin):
    list_display = ("user", "visitor", "count", "created", "modified",)
    list_filter = ("modified", "created",)
    date_hierarchy = "created"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    # def has_change_permission(self, request, obj=None):
    #     return False

    def has_module_permission(self, request):
        return True
