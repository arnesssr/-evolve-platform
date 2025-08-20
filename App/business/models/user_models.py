from django.contrib.auth.models import User
from django.db import models
from App.models import Business

class Department(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.business.name})"


class Software(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class BusinessUser(models.Model):
    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("manager", "Manager"),
        ("employee", "Employee"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("pending", "Pending"),
        ("suspended", "Suspended"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="business_profile")
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="users")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="employee")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    software_access = models.ManyToManyField(Software, blank=True)

    last_active = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # mirrors status for convenience

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.business.name}"