from django.db import models
from django.contrib.auth import get_user_model
from .subscription import Subscription

class SubscriptionUser(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('USER', 'Regular User'),
        ('VIEWER', 'View Only')
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    last_active = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['subscription', 'user']