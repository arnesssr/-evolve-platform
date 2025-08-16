from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import random
import string

class OTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    purpose = models.CharField(
    max_length=20,
    choices=[
        ("login", "Login"),
        ("register", "Register"),
        ("password_reset", "Password Reset"),
    ]
)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    def __str__(self):
        return f"{self.email} - {self.code} - {self.purpose}"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("business_owner", "Business Owner"),
        ("reseller", "Reseller"),
        ("admin", "Admin"),
        ("pending", "Pending Role")
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="pending")
    industry = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.email

    
class Business(models.Model):
    INDUSTRY_CHOICES = [
        ("Agriculture", "Agriculture"),
        ("Construction", "Construction"),
        ("Education", "Education"),
        ("Finance", "Finance"),
        ("Healthcare", "Healthcare"),
        ("Hospitality", "Hospitality"),
        ("Information Technology", "Information Technology"),
        ("Manufacturing", "Manufacturing"),
        ("Retail", "Retail"),
        ("Transportation & Logistics", "Transportation & Logistics"),
        ("Other", "Other"),
    ]

    COMPANY_SIZE_CHOICES = [
        ("1-10", "1-10"),
        ("11-50", "11-50"),
        ("51-200", "51-200"),
        ("200+", "200+"),
    ]

    COUNTRY_CHOICES = [
        ("Kenya", "Kenya"),
        ("Algeria", "Algeria"),
        ("Angola", "Angola"),
        ("Benin", "Benin"),
        ("Botswana", "Botswana"),
        ("Burkina Faso", "Burkina Faso"),
        ("Burundi", "Burundi"),
        ("Cabo Verde", "Cabo Verde"),
        ("Cameroon", "Cameroon"),
        ("Central African Republic", "Central African Republic"),
        ("Chad", "Chad"),
        ("Comoros", "Comoros"),
        ("Congo, Democratic Republic of the", "Congo, Democratic Republic of the"),
        ("Congo, Republic of the", "Congo, Republic of the"),
        ("Côte d'Ivoire", "Côte d'Ivoire"),
        ("Djibouti", "Djibouti"),
        ("Egypt", "Egypt"),
        ("Equatorial Guinea", "Equatorial Guinea"),
        ("Eritrea", "Eritrea"),
        ("Eswatini", "Eswatini"),
        ("Ethiopia", "Ethiopia"),
        ("Gabon", "Gabon"),
        ("Gambia", "Gambia"),
        ("Ghana", "Ghana"),
        ("Guinea", "Guinea"),
        ("Guinea-Bissau", "Guinea-Bissau"),
        ("Lesotho", "Lesotho"),
        ("Liberia", "Liberia"),
        ("Libya", "Libya"),
        ("Madagascar", "Madagascar"),
        ("Malawi", "Malawi"),
        ("Mali", "Mali"),
        ("Mauritania", "Mauritania"),
        ("Mauritius", "Mauritius"),
        ("Morocco", "Morocco"),
        ("Mozambique", "Mozambique"),
        ("Namibia", "Namibia"),
        ("Niger", "Niger"),
        ("Nigeria", "Nigeria"),
        ("Rwanda", "Rwanda"),
        ("Sao Tome and Principe", "Sao Tome and Principe"),
        ("Senegal", "Senegal"),
        ("Seychelles", "Seychelles"),
        ("Sierra Leone", "Sierra Leone"),
        ("Somalia", "Somalia"),
        ("South Africa", "South Africa"),
        ("South Sudan", "South Sudan"),
        ("Sudan", "Sudan"),
        ("Tanzania", "Tanzania"),
        ("Togo", "Togo"),
        ("Tunisia", "Tunisia"),
        ("Uganda", "Uganda"),
        ("Zambia", "Zambia"),
        ("Zimbabwe", "Zimbabwe")
    ]

    business_name = models.CharField(max_length=100)
    business_email = models.EmailField()
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES)
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES)
    postal_code = models.CharField(max_length=20)


    def __str__(self):
        return self.business_name

class Plan(models.Model):
    name = models.CharField(max_length=100)
    badge = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Feature(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.plan.name}"
