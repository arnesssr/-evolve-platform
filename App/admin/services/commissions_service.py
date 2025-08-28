"""
Admin Commissions Service
Extends reseller commission functionality for admin-wide operations, bulk actions, and management.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from django.db import transaction
from django.contrib.auth import get_user_model

from App.reseller.earnings.services.commission_service import CommissionService
from App.admin.repositories.commissions_repository import CommissionsRepository

User = get_user_model()


class CommissionsService:
    """Admin service for commission management and operations"""
    
    def __init__(self):
        self.reseller_service = CommissionService()
        self.repository = CommissionsRepository()
    
    def get_commissions_list(self, page: int = 1, page_size: int = 25, 
                           filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get paginated list of commissions with filtering
        
        Args:
            page: Page number
            page_size: Items per page
            filters: Dictionary of filters to apply
            
        Returns:
            Dictionary containing paginated results and summary
        """
        try:
            return self.repository.get_commissions_list(page, page_size, filters or {})
            
        except Exception as e:
            raise Exception(f"Error getting commissions list: {str(e)}")
    
    def approve_commissions(self, commission_ids: List[int], user: User) -> List[Dict[str, Any]]:
        """
        Approve multiple commissions
        
        Args:
            commission_ids: List of commission IDs to approve
            user: User performing the action
            
        Returns:
            List of results for each commission
        """
        results = []
        
        try:
            with transaction.atomic():
                for commission_id in commission_ids:
                    try:
                        # Use reseller service for the actual approval
                        commission = self.reseller_service.approve_commission(commission_id, user)
                        results.append({
                            'id': commission_id,
                            'success': True,
                            'commission': commission
                        })
                    except Exception as e:
                        results.append({
                            'id': commission_id,
                            'success': False,
                            'error': str(e)
                        })
            
            return results
            
        except Exception as e:
            raise Exception(f"Error approving commissions: {str(e)}")
    
    def reject_commissions(self, commission_ids: List[int], reason: str, user: User) -> List[Dict[str, Any]]:
        """
        Reject multiple commissions
        
        Args:
            commission_ids: List of commission IDs to reject
            reason: Reason for rejection
            user: User performing the action
            
        Returns:
            List of results for each commission
        """
        results = []
        
        try:
            with transaction.atomic():
                for commission_id in commission_ids:
                    try:
                        # Use reseller service for the actual rejection
                        commission = self.reseller_service.reject_commission(commission_id, reason, user)
                        results.append({
                            'id': commission_id,
                            'success': True,
                            'commission': commission
                        })
                    except Exception as e:
                        results.append({
                            'id': commission_id,
                            'success': False,
                            'error': str(e)
                        })
            
            return results
            
        except Exception as e:
            raise Exception(f"Error rejecting commissions: {str(e)}")
    
    def pay_commissions(self, commission_ids: List[int], payment_method: str, user: User) -> List[Dict[str, Any]]:
        """
        Mark multiple commissions as paid
        
        Args:
            commission_ids: List of commission IDs to mark as paid
            payment_method: Payment method used
            user: User performing the action
            
        Returns:
            List of results for each commission
        """
        results = []
        
        try:
            with transaction.atomic():
                for commission_id in commission_ids:
                    try:
                        # Use reseller service for the actual payment
                        commission = self.reseller_service.pay_commission(
                            commission_id, payment_method, user
                        )
                        results.append({
                            'id': commission_id,
                            'success': True,
                            'commission': commission
                        })
                    except Exception as e:
                        results.append({
                            'id': commission_id,
                            'success': False,
                            'error': str(e)
                        })
            
            return results
            
        except Exception as e:
            raise Exception(f"Error paying commissions: {str(e)}")
    
    def approve_filtered_commissions(self, filters: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Approve commissions matching filters
        
        Args:
            filters: Dictionary of filters to apply
            user: User performing the action
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Get commission IDs matching filters
            commission_ids = self.repository.get_commission_ids_by_filters(filters)
            
            # Limit to avoid accidental mass operations
            if len(commission_ids) > 100:
                raise Exception("Too many commissions selected. Please refine your filters.")
            
            results = self.approve_commissions(commission_ids, user)
            
            return {
                'processed_count': len([r for r in results if r['success']]),
                'failed_count': len([r for r in results if not r['success']]),
                'total_selected': len(commission_ids)
            }
            
        except Exception as e:
            raise Exception(f"Error approving filtered commissions: {str(e)}")
    
    def create_commission(self, reseller_id: int, amount: float, commission_type: str,
                         description: str = '', metadata: Dict[str, Any] = None, 
                         created_by: User = None) -> Any:
        """
        Create new commission
        
        Args:
            reseller_id: ID of the reseller
            amount: Commission amount
            commission_type: Type of commission
            description: Commission description
            metadata: Additional metadata
            created_by: User creating the commission
            
        Returns:
            Created commission instance
        """
        try:
            return self.reseller_service.create_commission(
                reseller_id=reseller_id,
                amount=amount,
                commission_type=commission_type,
                description=description,
                metadata=metadata or {},
                created_by=created_by
            )
            
        except Exception as e:
            raise Exception(f"Error creating commission: {str(e)}")
    
    def export_commissions(self, filters: Dict[str, Any] = None, format: str = 'csv',
                          fields: List[str] = None) -> Dict[str, Any]:
        """
        Export commissions to specified format
        
        Args:
            filters: Dictionary of filters to apply
            format: Export format ('csv', 'xlsx')
            fields: List of fields to include
            
        Returns:
            Dictionary containing export data
        """
        try:
            return self.repository.export_commissions(
                filters=filters or {},
                format=format,
                fields=fields or []
            )
            
        except Exception as e:
            raise Exception(f"Error exporting commissions: {str(e)}")
    
    def export_filtered_commissions(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export commissions matching filters
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            Dictionary containing export information
        """
        try:
            return self.export_commissions(filters=filters, format='xlsx')
            
        except Exception as e:
            raise Exception(f"Error exporting filtered commissions: {str(e)}")
    
    def get_commission_detail(self, commission_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed commission information
        
        Args:
            commission_id: ID of the commission
            
        Returns:
            Dictionary containing commission details or None if not found
        """
        try:
            return self.repository.get_commission_detail(commission_id)
            
        except Exception as e:
            raise Exception(f"Error getting commission detail: {str(e)}")
    
    def get_commission_statistics(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get commission statistics for admin dashboard
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            Dictionary containing commission statistics
        """
        try:
            return self.repository.get_commission_statistics(filters or {})
            
        except Exception as e:
            raise Exception(f"Error getting commission statistics: {str(e)}")
