"""
Admin Payouts Service
Extends reseller payout functionality for admin-wide operations and management.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from django.db import transaction
from django.contrib.auth import get_user_model

from App.reseller.earnings.services.payout_service import PayoutService
from App.admin.repositories.payouts_repository import PayoutsRepository

User = get_user_model()


class PayoutsService:
    """Admin service for payout management and operations"""
    
    def __init__(self):
        self.reseller_service = PayoutService()
        self.repository = PayoutsRepository()
    
    def get_payouts_list(self, page: int = 1, page_size: int = 25, 
                        filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get paginated list of payouts with filtering"""
        try:
            return self.repository.get_payouts_list(page, page_size, filters or {})
        except Exception as e:
            raise Exception(f"Error getting payouts list: {str(e)}")
    
    def process_payouts(self, payout_ids: List[int], payment_method: str, user: User) -> List[Dict[str, Any]]:
        """Process multiple payouts"""
        results = []
        try:
            with transaction.atomic():
                for payout_id in payout_ids:
                    try:
                        result = self.reseller_service.process_payout(payout_id, payment_method, user)
                        results.append({
                            'id': payout_id,
                            'success': True,
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'id': payout_id,
                            'success': False,
                            'error': str(e)
                        })
            return results
        except Exception as e:
            raise Exception(f"Error processing payouts: {str(e)}")
    
    def complete_payouts(self, payout_ids: List[int], transaction_id: str, 
                        completion_date: str, user: User) -> List[Dict[str, Any]]:
        """Mark multiple payouts as completed"""
        results = []
        try:
            with transaction.atomic():
                for payout_id in payout_ids:
                    try:
                        result = self.reseller_service.complete_payout(
                            payout_id, transaction_id, completion_date, user
                        )
                        results.append({
                            'id': payout_id,
                            'success': True,
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'id': payout_id,
                            'success': False,
                            'error': str(e)
                        })
            return results
        except Exception as e:
            raise Exception(f"Error completing payouts: {str(e)}")
    
    def fail_payouts(self, payout_ids: List[int], reason: str, user: User) -> List[Dict[str, Any]]:
        """Mark multiple payouts as failed"""
        results = []
        try:
            with transaction.atomic():
                for payout_id in payout_ids:
                    try:
                        result = self.reseller_service.fail_payout(payout_id, reason, user)
                        results.append({
                            'id': payout_id,
                            'success': True,
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'id': payout_id,
                            'success': False,
                            'error': str(e)
                        })
            return results
        except Exception as e:
            raise Exception(f"Error failing payouts: {str(e)}")
    
    def retry_payouts(self, payout_ids: List[int], user: User) -> List[Dict[str, Any]]:
        """Retry multiple failed payouts"""
        results = []
        try:
            with transaction.atomic():
                for payout_id in payout_ids:
                    try:
                        result = self.reseller_service.retry_payout(payout_id, user)
                        results.append({
                            'id': payout_id,
                            'success': True,
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'id': payout_id,
                            'success': False,
                            'error': str(e)
                        })
            return results
        except Exception as e:
            raise Exception(f"Error retrying payouts: {str(e)}")
    
    def cancel_payouts(self, payout_ids: List[int], reason: str, user: User) -> List[Dict[str, Any]]:
        """Cancel multiple payouts"""
        results = []
        try:
            with transaction.atomic():
                for payout_id in payout_ids:
                    try:
                        result = self.reseller_service.cancel_payout(payout_id, reason, user)
                        results.append({
                            'id': payout_id,
                            'success': True,
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'id': payout_id,
                            'success': False,
                            'error': str(e)
                        })
            return results
        except Exception as e:
            raise Exception(f"Error cancelling payouts: {str(e)}")
    
    def create_payout(self, reseller_id: int, amount: float, method: str,
                     description: str = '', payment_details: Dict[str, Any] = None,
                     created_by: User = None) -> Any:
        """Create new payout"""
        try:
            return self.reseller_service.create_payout(
                reseller_id=reseller_id,
                amount=amount,
                method=method,
                description=description,
                payment_details=payment_details or {},
                created_by=created_by
            )
        except Exception as e:
            raise Exception(f"Error creating payout: {str(e)}")
    
    def process_filtered_payouts(self, filters: Dict[str, Any], payment_method: str, 
                                user: User) -> Dict[str, Any]:
        """Process payouts matching filters"""
        try:
            payout_ids = self.repository.get_payout_ids_by_filters(filters)
            if len(payout_ids) > 50:
                raise Exception("Too many payouts selected. Please refine your filters.")
            
            results = self.process_payouts(payout_ids, payment_method, user)
            return {
                'processed_count': len([r for r in results if r['success']]),
                'failed_count': len([r for r in results if not r['success']]),
                'total_selected': len(payout_ids)
            }
        except Exception as e:
            raise Exception(f"Error processing filtered payouts: {str(e)}")
    
    def export_filtered_payouts(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Export payouts matching filters"""
        try:
            return self.repository.export_payouts(filters=filters, format='xlsx')
        except Exception as e:
            raise Exception(f"Error exporting filtered payouts: {str(e)}")
    
    def export_payouts(self, filters: Dict[str, Any] = None, format: str = 'csv',
                      fields: List[str] = None) -> Dict[str, Any]:
        """Export payouts to specified format"""
        try:
            return self.repository.export_payouts(
                filters=filters or {},
                format=format,
                fields=fields or []
            )
        except Exception as e:
            raise Exception(f"Error exporting payouts: {str(e)}")
    
    def get_payout_detail(self, payout_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed payout information"""
        try:
            return self.repository.get_payout_detail(payout_id)
        except Exception as e:
            raise Exception(f"Error getting payout detail: {str(e)}")
    
    def create_commission_based_payouts(self, min_amount: float = 0, 
                                       reseller_ids: List[int] = None,
                                       created_by: User = None) -> Dict[str, Any]:
        """Create payouts based on approved commissions"""
        try:
            return self.reseller_service.create_commission_based_payouts(
                min_amount=min_amount,
                reseller_ids=reseller_ids or [],
                created_by=created_by
            )
        except Exception as e:
            raise Exception(f"Error creating commission-based payouts: {str(e)}")
    
    def create_manual_batch_payouts(self, payouts_data: List[Dict[str, Any]], 
                                   created_by: User = None) -> Dict[str, Any]:
        """Create batch of manual payouts"""
        try:
            results = []
            created_count = 0
            failed_count = 0
            total_amount = 0
            payout_ids = []
            
            for payout_data in payouts_data:
                try:
                    payout = self.create_payout(
                        reseller_id=payout_data['reseller_id'],
                        amount=payout_data['amount'],
                        method=payout_data['method'],
                        description=payout_data.get('description', ''),
                        payment_details=payout_data.get('payment_details', {}),
                        created_by=created_by
                    )
                    created_count += 1
                    total_amount += payout_data['amount']
                    payout_ids.append(payout.id)
                    
                except Exception as e:
                    failed_count += 1
                    results.append({
                        'reseller_id': payout_data['reseller_id'],
                        'error': str(e)
                    })
            
            return {
                'created_count': created_count,
                'failed_count': failed_count,
                'total_amount': total_amount,
                'payout_ids': payout_ids,
                'errors': results
            }
            
        except Exception as e:
            raise Exception(f"Error creating manual batch payouts: {str(e)}")
