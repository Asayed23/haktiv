from rest_framework import serializers

from ...models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("created", "guid", "user", "read", "title", "body", "category",)


class NotificationEmptySerializer(serializers.Serializer):
    pass


class NotificationListSerializer(serializers.Serializer):
    category = serializers.ChoiceField(choices=Notification.CATEGORIES, allow_blank=True, required=False)


class NotificationMarkAsReadOrUnreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("read",)
