from django.utils.translation import ugettext as _
from rest_framework import serializers

from ...models import UserSocialMedia

class UserSocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocialMedia
        fields = ("user", "link", "social",)
        lookup_field = "guid"
        extra_kwargs = {
            "url": {"lookup_field": "guid"}
        }