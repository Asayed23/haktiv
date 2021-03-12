from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.admin import GroupAdmin as AuthGroupAdmin


class Group(AuthGroup):
    class Meta:
        proxy = True


admin.site.unregister(AuthGroup)


@admin.register(Group)
class GroupAdmin(AuthGroupAdmin):
    pass