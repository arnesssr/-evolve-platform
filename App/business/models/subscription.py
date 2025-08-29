from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Subscription(models.Model):
    SOFTWARE_CHOICES = [
        ('ERP', 'ERP System'),
        ('SACCO', 'SACCO Platform'),
        ('PAYROLL', 'Payroll System')
    ]
    
    PLAN_CHOICES = [
        ('STANDARD', 'Standard'),
        ('PROFESSIONAL', 'Professional'),
        ('ENTERPRISE', 'Enterprise'),
        ('PREMIUM', 'Premium')
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('PENDING', 'Pending')
    ]

    business = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    software_type = models.CharField(max_length=20, choices=SOFTWARE_CHOICES)
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    max_users = models.IntegerField()
    active_users = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'business_subscriptions'

    def get_usage_percentage(self):
        return (self.active_users / self.max_users * 100) if self.max_users > 0 else 0

    def days_until_expiry(self):
        return (self.end_date - timezone.now()).days