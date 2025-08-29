from ..models.notification import Notification
from django.contrib.contenttypes.models import ContentType

class NotificationRepository:
    @staticmethod
    def create_notification(recipient, notification_type, title, message, related_object):
        content_type = ContentType.objects.get_for_model(related_object)
        return Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            content_type=content_type,
            object_id=related_object.id
        )
    
    @staticmethod
    def get_user_notifications(user, unread_only=False):
        queryset = Notification.objects.filter(recipient=user)
        if unread_only:
            queryset = queryset.filter(is_read=False)
        return queryset
    
    @staticmethod
    def mark_as_read(notification_id):
        Notification.objects.filter(id=notification_id).update(is_read=True)