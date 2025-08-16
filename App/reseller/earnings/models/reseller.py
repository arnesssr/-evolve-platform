"""Reseller profile model."""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from .base import TimeStampedModel, TierChoices

User = get_user_model()


class ResellerType(models.TextChoices):
    INDIVIDUAL = 'individual', 'Individual Affiliate'
    BUSINESS = 'business', 'Business Partner'

class Reseller(TimeStampedModel):
    """Reseller profile model."""
    # User relationship
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='reseller_profile'
    )

    # Reseller type
    reseller_type = models.CharField(
        max_length=20,
        choices=ResellerType.choices,
        default=ResellerType.INDIVIDUAL
    )
    
    # Company information
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    company_description = models.TextField(blank=True)
    
    # Contact information
    phone_number = models.CharField(max_length=20, blank=True)
    alternate_email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Reseller details
    referral_code = models.CharField(max_length=50, unique=True, db_index=True)
    tier = models.CharField(
        max_length=20,
        choices=TierChoices.choices,
        default=TierChoices.BRONZE
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Financial information
    payment_method = models.CharField(max_length=50, blank=True)
    bank_account_name = models.CharField(max_length=255, blank=True)
    bank_account_number = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    bank_routing_number = models.CharField(max_length=50, blank=True)
    paypal_email = models.EmailField(blank=True)
    
    # Status and verification
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Metrics
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_commission_earned = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_commission_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    pending_commission = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Join date tracking
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reseller_profiles'
        verbose_name = 'Reseller'
        verbose_name_plural = 'Resellers'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.company_name or 'Individual'}"
    
    def get_available_balance(self):
        """Calculate available balance for withdrawal."""
        return self.pending_commission
    
    def get_tier_commission_rate(self):
        """Get commission rate based on tier."""
        tier_rates = {
            TierChoices.BRONZE: Decimal('10.00'),
            TierChoices.SILVER: Decimal('15.00'),
            TierChoices.GOLD: Decimal('20.00'),
            TierChoices.PLATINUM: Decimal('25.00'),
        }
        return tier_rates.get(self.tier, self.commission_rate)
    
    def update_tier(self):
        """Update reseller tier based on total sales."""
        if self.total_sales >= 50000:
            self.tier = TierChoices.PLATINUM
            self.commission_rate = Decimal('25.00')
        elif self.total_sales >= 15000:
            self.tier = TierChoices.GOLD
            self.commission_rate = Decimal('20.00')
        elif self.total_sales >= 5000:
            self.tier = TierChoices.SILVER
            self.commission_rate = Decimal('15.00')
        else:
            self.tier = TierChoices.BRONZE
            self.commission_rate = Decimal('10.00')
        self.save(update_fields=['tier', 'commission_rate'])
    
    @classmethod
    def generate_unique_referral_code(cls, user_id):
        """Generate a unique referral code, ensuring no duplicates."""
        from myapp.reseller.utils import generate_partner_code
        
        max_attempts = 10
        for _ in range(max_attempts):
            code = generate_partner_code(user_id)
            if not cls.objects.filter(referral_code=code).exists():
                return code
        
        # If we couldn't generate a unique code after max_attempts,
        # append a timestamp to ensure uniqueness
        import time
        return f"{code}-{int(time.time())}"
