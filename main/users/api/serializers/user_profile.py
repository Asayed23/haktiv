from rest_framework import serializers

from main.users.models import User


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)                                                           


class UserProfileSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        # exclude = ("password", "last_login", "is_superuser", "is_staff", "created", "modified", "groups", "user_permissions")

