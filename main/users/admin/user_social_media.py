from django.contrib import admin

from ..models import UserSocialMedia


class UserSocialMediaAdmin(UserSocialMedia):
    class Meta:
        proxy = True


# admin.site.unregister(UserSocialMedia)


# Register your models here.
class UserSocialMediaAdmin(admin.ModelAdmin):
    # list_display = ['__str__','vendor','serial']
    # class Meta:
    pass
# admin.site.register(pki_record,pki_record_admin)
admin.site.register(UserSocialMedia)

# @admin.register(UserSocialMediaAdmin) 
# class UserSocialMediaAdmin(UserSocialMediaAdmin):
#     pass