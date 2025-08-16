"""Context processors for reseller app"""
from .earnings.models import Reseller


def reseller_context(request):
    """Add reseller-specific context to all templates"""
    context = {}
    
    if request.user.is_authenticated:
        try:
            reseller = Reseller.objects.get(user=request.user)
            context['partner_code'] = reseller.referral_code
            context['reseller'] = reseller
        except Reseller.DoesNotExist:
            # If reseller profile doesn't exist, don't add partner_code
            pass
    
    return context
