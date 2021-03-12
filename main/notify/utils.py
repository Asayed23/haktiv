from main.notify.models import Notification


def get_user_channel(user):
    """[Get User WS Channel]

    Args:
        user ([UserObject]): [User Object]

    Returns:
        [string]: [user ws channel]
    """
    return str(user)


def call_latest_notifications(user, limit=5):
    """[Get Latest Notification]

    Args:
        user ([UserObject]): [User Object]
        limit (int, optional): [limit to you return]. Defaults to 5.

    Returns:
        [QuerySet]: [notifications QuerySet]
    """
    notifications = Notification.objects.filter(user=user, read=False)
    return notifications[:int(limit)]