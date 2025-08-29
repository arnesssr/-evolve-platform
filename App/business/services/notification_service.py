from ..repositories.notification_repository import NotificationRepository
from django.utils import timezone
from datetime import timedelta

class NotificationService:
    def __init__(self):
        self.repository = NotificationRepository()

    def send_expiry_notification(self, subscription):
        days_left = (subscription.end_date - timezone.now()).days
        
        if days_left <= 30:
            title = f"Subscription Expiring Soon"
            message = f"Your {subscription.software_type} subscription will expire in {days_left} days."
            self.repository.create_notification(
                recipient=subscription.business,
                notification_type='EXPIRY',
                title=title,
                message=message,
                related_object=subscription
            )

    def send_usage_alert(self, subscription):
        usage_percentage = subscription.get_usage_percentage()
        if usage_percentage >= 90:
            title = "High Usage Alert"
            message = f"Your {subscription.software_type} subscription has reached {usage_percentage}% of user limit."
            self.repository.create_notification(
                recipient=subscription.business,
                notification_type='USAGE',
                title=title,
                message=message,
                related_object=subscription
            )

    def send_payment_reminder(self, invoice):
        if not invoice.is_paid and invoice.due_date <= timezone.now().date() + timedelta(days=7):
            title = "Payment Reminder"
            message = f"Invoice {invoice.invoice_number} for {invoice.amount} is due on {invoice.due_date}."
            self.repository.create_notification(
                recipient=invoice.subscription.business,
                notification_type='PAYMENT',
                title=title,
                message=message,
                related_object=invoice
            )