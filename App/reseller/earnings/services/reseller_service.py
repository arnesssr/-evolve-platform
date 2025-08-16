"""Reseller profile service for business logic operations."""
from typing import Dict, Optional, List, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal
import logging

from ..models.reseller import Reseller
from ..repositories.reseller_repository import ResellerRepository
from .base import BaseService

User = get_user_model()
logger = logging.getLogger(__name__)


class ResellerService(BaseService):
    """Service for managing reseller profiles and operations."""
    
    def __init__(self):
        super().__init__()
        self.repository = ResellerRepository()
    
    @transaction.atomic
    def create_reseller_profile(self, user: User, profile_data: Dict[str, Any]) -> Reseller:
        """
        Create a new reseller profile for a user.
        
        Args:
            user: User instance
            profile_data: Dictionary containing profile information
            
        Returns:
            Created Reseller instance
        """
        try:
            # Check if profile already exists
            if hasattr(user, 'reseller_profile'):
                raise ValidationError(f"User {user.username} already has a reseller profile")
            
            # Generate unique referral code
            referral_code = Reseller.generate_unique_referral_code(user.id)
            
            # Create profile
            profile_data['user'] = user
            profile_data['referral_code'] = referral_code
            
            reseller = self.repository.create(**profile_data)
            
            logger.info(f"Created reseller profile for user {user.username}")
            return reseller
            
        except Exception as e:
            logger.error(f"Error creating reseller profile: {str(e)}")
            raise
    
    @transaction.atomic
    def update_profile(self, reseller_id: int, profile_data: Dict[str, Any]) -> Reseller:
        """
        Update reseller profile information.
        
        Args:
            reseller_id: ID of the reseller
            profile_data: Dictionary containing updated profile information
            
        Returns:
            Updated Reseller instance
        """
        try:
            reseller = self.repository.get_by_id(reseller_id)
            
            # Update allowed fields
            allowed_fields = [
                'company_name', 'company_website', 'company_description',
                'phone_number', 'alternate_email', 'address', 'city',
                'state', 'country', 'postal_code', 'payment_method',
                'bank_account_name', 'bank_account_number', 'bank_name',
                'bank_routing_number', 'paypal_email'
            ]
            
            update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
            
            reseller = self.repository.update(reseller_id, **update_data)
            
            logger.info(f"Updated profile for reseller {reseller_id}")
            return reseller
            
        except Exception as e:
            logger.error(f"Error updating reseller profile: {str(e)}")
            raise
    
    def verify_reseller(self, reseller_id: int) -> Reseller:
        """
        Verify a reseller's profile.
        
        Args:
            reseller_id: ID of the reseller
            
        Returns:
            Updated Reseller instance
        """
        try:
            reseller = self.repository.verify_reseller(reseller_id)
            logger.info(f"Verified reseller {reseller_id}")
            return reseller
        except Exception as e:
            logger.error(f"Error verifying reseller: {str(e)}")
            raise
    
    def get_profile_completion_status(self, reseller_id: int) -> Dict[str, Any]:
        """
        Calculate profile completion percentage and missing fields.
        
        Args:
            reseller_id: ID of the reseller
            
        Returns:
            Dictionary with completion status
        """
        reseller = self.repository.get_by_id(reseller_id)
        
        required_fields = {
            'company_name': 'Company Name',
            'phone_number': 'Phone Number',
            'address': 'Address',
            'city': 'City',
            'state': 'State',
            'country': 'Country',
            'payment_method': 'Payment Method'
        }
        
        optional_fields = {
            'company_website': 'Company Website',
            'company_description': 'Company Description',
            'alternate_email': 'Alternate Email',
            'postal_code': 'Postal Code'
        }
        
        # Check payment method specific fields
        if reseller.payment_method == 'bank_transfer':
            required_fields.update({
                'bank_account_name': 'Bank Account Name',
                'bank_account_number': 'Bank Account Number',
                'bank_name': 'Bank Name'
            })
        elif reseller.payment_method == 'paypal':
            required_fields['paypal_email'] = 'PayPal Email'
        
        missing_required = []
        missing_optional = []
        
        for field, label in required_fields.items():
            if not getattr(reseller, field):
                missing_required.append(label)
        
        for field, label in optional_fields.items():
            if not getattr(reseller, field):
                missing_optional.append(label)
        
        total_fields = len(required_fields) + len(optional_fields)
        completed_fields = total_fields - len(missing_required) - len(missing_optional)
        completion_percentage = int((completed_fields / total_fields) * 100)
        
        return {
            'completion_percentage': completion_percentage,
            'is_complete': len(missing_required) == 0,
            'missing_required': missing_required,
            'missing_optional': missing_optional,
            'total_fields': total_fields,
            'completed_fields': completed_fields
        }
    
    def update_tier_status(self, reseller_id: int) -> Reseller:
        """
        Update reseller tier based on performance metrics.
        
        Args:
            reseller_id: ID of the reseller
            
        Returns:
            Updated Reseller instance
        """
        try:
            reseller = self.repository.get_by_id(reseller_id)
            old_tier = reseller.tier
            
            reseller.update_tier()
            
            if old_tier != reseller.tier:
                logger.info(f"Updated reseller {reseller_id} tier from {old_tier} to {reseller.tier}")
            
            return reseller
        except Exception as e:
            logger.error(f"Error updating reseller tier: {str(e)}")
            raise
    
    def get_reseller_by_referral_code(self, referral_code: str) -> Optional[Reseller]:
        """
        Get reseller by referral code.
        
        Args:
            referral_code: Referral code
            
        Returns:
            Reseller instance or None
        """
        return self.repository.get_by_referral_code(referral_code)
    
    def get_reseller_stats(self, reseller_id: int) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a reseller.
        
        Args:
            reseller_id: ID of the reseller
            
        Returns:
            Dictionary with reseller statistics
        """
        reseller = self.repository.get_by_id(reseller_id)
        
        return {
            'total_sales': reseller.total_sales,
            'total_commission_earned': reseller.total_commission_earned,
            'total_commission_paid': reseller.total_commission_paid,
            'pending_commission': reseller.pending_commission,
            'available_balance': reseller.get_available_balance(),
            'tier': reseller.tier,
            'commission_rate': reseller.commission_rate,
            'is_verified': reseller.is_verified,
            'profile_completion': self.get_profile_completion_status(reseller_id)
        }
    
    def search_resellers(self, filters: Dict[str, Any]) -> List[Reseller]:
        """
        Search resellers based on filters.
        
        Args:
            filters: Dictionary of search filters
            
        Returns:
            List of Reseller instances
        """
        return self.repository.search(filters)
    
    def deactivate_reseller(self, reseller_id: int) -> Reseller:
        """
        Deactivate a reseller profile.
        
        Args:
            reseller_id: ID of the reseller
            
        Returns:
            Updated Reseller instance
        """
        try:
            reseller = self.repository.update(reseller_id, is_active=False)
            logger.info(f"Deactivated reseller {reseller_id}")
            return reseller
        except Exception as e:
            logger.error(f"Error deactivating reseller: {str(e)}")
            raise
    
    def activate_reseller(self, reseller_id: int) -> Reseller:
        """
        Activate a reseller profile.
        
        Args:
            reseller_id: ID of the reseller
            
        Returns:
            Updated Reseller instance
        """
        try:
            reseller = self.repository.update(reseller_id, is_active=True)
            logger.info(f"Activated reseller {reseller_id}")
            return reseller
        except Exception as e:
            logger.error(f"Error activating reseller: {str(e)}")
            raise
