from django.contrib import admin

from main.core.utils import get_user_search_fields
from ..models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "read", "created",)
    list_filter = ("category",)
    search_fields = ("title",) + get_user_search_fields(field_name="user")
    readonly_fields = ("read", "from_user", "user", "category",)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        return super(NotificationAdmin, self).save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return False
