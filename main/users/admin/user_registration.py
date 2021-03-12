from django.utils.translation import gettext, gettext_lazy as _
from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.contrib import messages

from ..models import RegisteredUser
from ..forms import RegisteredUserAdminForm

@admin.register(RegisteredUser)
class RegisteredUserAdmin(admin.ModelAdmin):
    form = RegisteredUserAdminForm
    change_form_template = "admin/registration_action.html"
    list_display = ("full_name", "company_name", "display_password", "email", "country", "role",
                    "display_status", "phone",)
    list_filter = ("role", "status", "country",)
    search_fields = ("first_name", "last_name", "company_name", "email",)
    _readonly_fields = ("full_name", "display_password", "status",)
    fieldsets = (
        (None, {'fields': ("full_name", "company_name", "display_password", "email", "country", "role",
                           "status", "phone", "linkedin_profile", "role_name", "message",)},),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'company_name', "password", "email", "country", "role",
                       "status", "phone", "linkedin_profile", "role_name",),
        }),
    )
    def get_fieldsets(self, request, obj=None):
        if not obj:
            self.readonly_fields = self._readonly_fields
            return self.add_fieldsets
        self.readonly_fields = self._readonly_fields + ("company_name", "email", "phone", "country", "role",)
        return super(RegisteredUserAdmin, self).get_fieldsets(request, obj)

    def display_status(self, obj):
        if obj.status == RegisteredUser.PENDING:
            text = '<strong style="color:#f1c40f;">{}</strong>'.format(obj.get_status_display())
        elif obj.status == RegisteredUser.APPROVED:
            text = '<strong style="color:#2ecc71;">{}</strong>'.format(obj.get_status_display())
        else:
            text = '<strong style="color:#e74c3c;">{}</strong>'.format(obj.get_status_display())
        return format_html("{}", mark_safe(text))

    def response_change(self, request, obj):
        try:
            if "create_user" in request.POST:
                obj.approve_user(message=request.POST.get("message"))
                obj.status = RegisteredUser.APPROVED
                obj.save()
                messages.success(request, "The application has been added to system successfully")
            elif "rejected_user" in request.POST:
                obj.reject_user(message=request.POST.get("message"))
                obj.status = RegisteredUser.REJECTED
                obj.save()
                messages.success(request, "The application has been rejected from system successfully")
        except Exception as e:
            messages.warning(request, f"An error occured {e}")
        return super(RegisteredUserAdmin, self).response_change(request, obj)