"""
Admin Invoices Service
Extends reseller invoice functionality for admin-wide operations and management.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from django.db import transaction
from django.contrib.auth import get_user_model

from App.reseller.earnings.services.invoice_service import InvoiceService
from App.admin.repositories.invoices_repository import InvoicesRepository

User = get_user_model()


class InvoicesService:
    """Admin service for invoice management and operations"""
    
    def __init__(self):
        self.reseller_service = InvoiceService()
        self.repository = InvoicesRepository()
    
    def get_invoices_list(self, page: int = 1, page_size: int = 25, 
                         filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get paginated list of invoices with filtering"""
        try:
            return self.repository.get_invoices_list(page, page_size, filters or {})
        except Exception as e:
            raise Exception(f"Error getting invoices list: {str(e)}")
    
    def create_invoice_from_commissions(self, commission_ids: List[int], created_by: User) -> Any:
        """Create invoice from approved commissions"""
        try:
            return self.reseller_service.create_invoice_from_commissions(
                commission_ids, created_by
            )
        except Exception as e:
            raise Exception(f"Error creating invoice from commissions: {str(e)}")
    
    def create_manual_invoice(self, business_id: int, amount: float, description: str,
                             due_date: str = None, metadata: Dict[str, Any] = None,
                             created_by: User = None) -> Any:
        """Create manual invoice"""
        try:
            return self.reseller_service.create_manual_invoice(
                business_id=business_id,
                amount=amount,
                description=description,
                due_date=due_date,
                metadata=metadata or {},
                created_by=created_by
            )
        except Exception as e:
            raise Exception(f"Error creating manual invoice: {str(e)}")
    
    def send_invoices(self, invoice_ids: List[int], email_template: str, user: User) -> List[Dict[str, Any]]:
        """Send multiple invoices"""
        results = []
        try:
            with transaction.atomic():
                for invoice_id in invoice_ids:
                    try:
                        result = self.reseller_service.send_invoice(invoice_id, email_template, user)
                        results.append({
                            'id': invoice_id,
                            'success': True,
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'id': invoice_id,
                            'success': False,
                            'error': str(e)
                        })
            return results
        except Exception as e:
            raise Exception(f"Error sending invoices: {str(e)}")
    
    def mark_invoices_paid(self, invoice_ids: List[int], payment_date: str,
                          payment_method: str, reference: str, user: User) -> List[Dict[str, Any]]:
        """Mark multiple invoices as paid"""
        results = []
        try:
            with transaction.atomic():
                for invoice_id in invoice_ids:
                    try:
                        result = self.reseller_service.mark_paid(
                            invoice_id, payment_date, payment_method, reference, user
                        )
                        results.append({
                            'id': invoice_id,
                            'success': True,
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'id': invoice_id,
                            'success': False,
                            'error': str(e)
                        })
            return results
        except Exception as e:
            raise Exception(f"Error marking invoices paid: {str(e)}")
    
    def cancel_invoices(self, invoice_ids: List[int], reason: str, user: User) -> List[Dict[str, Any]]:
        """Cancel multiple invoices"""
        results = []
        try:
            with transaction.atomic():
                for invoice_id in invoice_ids:
                    try:
                        result = self.reseller_service.cancel_invoice(invoice_id, reason, user)
                        results.append({
                            'id': invoice_id,
                            'success': True,
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'id': invoice_id,
                            'success': False,
                            'error': str(e)
                        })
            return results
        except Exception as e:
            raise Exception(f"Error cancelling invoices: {str(e)}")
    
    def regenerate_invoices(self, invoice_ids: List[int], user: User) -> List[Dict[str, Any]]:
        """Regenerate multiple invoices"""
        results = []
        try:
            with transaction.atomic():
                for invoice_id in invoice_ids:
                    try:
                        result = self.reseller_service.regenerate_invoice(invoice_id, user)
                        results.append({
                            'id': invoice_id,
                            'success': True,
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'id': invoice_id,
                            'success': False,
                            'error': str(e)
                        })
            return results
        except Exception as e:
            raise Exception(f"Error regenerating invoices: {str(e)}")
    
    def get_invoice_pdf(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Get invoice PDF data"""
        try:
            return self.reseller_service.generate_pdf(invoice_id)
        except Exception as e:
            raise Exception(f"Error getting invoice PDF: {str(e)}")
    
    def send_filtered_invoices(self, filters: Dict[str, Any], email_template: str, user: User) -> Dict[str, Any]:
        """Send invoices matching filters"""
        try:
            invoice_ids = self.repository.get_invoice_ids_by_filters(filters)
            if len(invoice_ids) > 100:
                raise Exception("Too many invoices selected. Please refine your filters.")
            
            results = self.send_invoices(invoice_ids, email_template, user)
            return {
                'processed_count': len([r for r in results if r['success']]),
                'failed_count': len([r for r in results if not r['success']]),
                'total_selected': len(invoice_ids)
            }
        except Exception as e:
            raise Exception(f"Error sending filtered invoices: {str(e)}")
    
    def export_filtered_invoices(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Export invoices matching filters"""
        try:
            return self.repository.export_invoices(filters=filters, format='xlsx')
        except Exception as e:
            raise Exception(f"Error exporting filtered invoices: {str(e)}")
    
    def export_invoices(self, filters: Dict[str, Any] = None, format: str = 'csv',
                       fields: List[str] = None) -> Dict[str, Any]:
        """Export invoices to specified format"""
        try:
            return self.repository.export_invoices(
                filters=filters or {},
                format=format,
                fields=fields or []
            )
        except Exception as e:
            raise Exception(f"Error exporting invoices: {str(e)}")
    
    def get_invoice_detail(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed invoice information"""
        try:
            return self.repository.get_invoice_detail(invoice_id)
        except Exception as e:
            raise Exception(f"Error getting invoice detail: {str(e)}")
