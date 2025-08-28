"""
Admin Commissions Repository
Handles data access for commission management and filtering.
"""

from typing import Dict, List, Any
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
import csv
import io

from App.reseller.earnings.models.commission import Commission


class CommissionsRepository:
    """Repository for commission-related data access"""
    
    def get_commissions_list(self, page: int, page_size: int, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get paginated commission list with filters"""
        try:
            queryset = Commission.objects.all().select_related('reseller')
            
            # Apply filters
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            if filters.get('reseller_id'):
                queryset = queryset.filter(reseller_id=filters['reseller_id'])
            if filters.get('min_amount'):
                queryset = queryset.filter(amount__gte=filters['min_amount'])
            if filters.get('max_amount'):
                queryset = queryset.filter(amount__lte=filters['max_amount'])
            if filters.get('start_date'):
                queryset = queryset.filter(created_at__gte=filters['start_date'])
            if filters.get('end_date'):
                queryset = queryset.filter(created_at__lte=filters['end_date'])
            if filters.get('search'):
                search = filters['search']
                queryset = queryset.filter(
                    Q(description__icontains=search) |
                    Q(reseller__name__icontains=search)
                )
            
            # Get summary data
            summary = queryset.aggregate(
                total_amount=Sum('amount'),
                pending_count=Count('id', filter=Q(status='pending')),
                approved_count=Count('id', filter=Q(status='approved')),
                paid_count=Count('id', filter=Q(status='paid'))
            )
            
            # Paginate
            paginator = Paginator(queryset.order_by('-created_at'), page_size)
            page_obj = paginator.get_page(page)
            
            # Serialize results
            results = []
            for commission in page_obj.object_list:
                results.append({
                    'id': commission.id,
                    'amount': float(commission.amount),
                    'status': commission.status,
                    'commission_rate': float(commission.commission_rate),
                    'description': getattr(commission, 'description', None) or commission.notes or commission.product_name,
                    'created_at': commission.created_at.isoformat(),
                    'reseller': {
                        'id': commission.reseller.id,
                        'name': commission.reseller.user.get_full_name() or commission.reseller.company_name or commission.reseller.user.username
                    } if commission.reseller else None
                })
            
            return {
                'results': results,
                'total_count': paginator.count,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'summary': {
                    'total_amount': float(summary['total_amount'] or 0),
                    'pending_count': summary['pending_count'],
                    'approved_count': summary['approved_count'],
                    'paid_count': summary['paid_count']
                }
            }
            
        except Exception as e:
            raise Exception(f"Error getting commissions list: {str(e)}")
    
    def get_commission_ids_by_filters(self, filters: Dict[str, Any]) -> List[int]:
        """Get commission IDs matching filters"""
        try:
            queryset = Commission.objects.all()
            
            # Apply same filters as get_commissions_list
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            if filters.get('reseller_id'):
                queryset = queryset.filter(reseller_id=filters['reseller_id'])
            if filters.get('min_amount'):
                queryset = queryset.filter(amount__gte=filters['min_amount'])
            if filters.get('max_amount'):
                queryset = queryset.filter(amount__lte=filters['max_amount'])
            if filters.get('start_date'):
                queryset = queryset.filter(created_at__gte=filters['start_date'])
            if filters.get('end_date'):
                queryset = queryset.filter(created_at__lte=filters['end_date'])
            
            return list(queryset.values_list('id', flat=True))
            
        except Exception as e:
            raise Exception(f"Error getting commission IDs by filters: {str(e)}")
    
    def export_commissions(self, filters: Dict[str, Any], format: str, fields: List[str]) -> Dict[str, Any]:
        """Export commissions matching filters"""
        try:
            queryset = Commission.objects.all().select_related('reseller')
            
            # Apply filters (same as get_commissions_list)
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            # ... other filters
            
            # Generate export file
            filename = f"commissions_export_{format}.{format}"
            
            if format == 'csv':
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(['ID', 'Amount', 'Status', 'Type', 'Reseller', 'Created'])
                
                for commission in queryset:
                    writer.writerow([
                        commission.id,
                        commission.amount,
                        commission.status,
                        commission.commission_rate,
                        (commission.reseller.user.get_full_name() or commission.reseller.company_name or commission.reseller.user.username) if commission.reseller else '',
                        commission.created_at.isoformat()
                    ])
                
                return {
                    'content': output.getvalue(),
                    'filename': filename,
                    'record_count': queryset.count()
                }
            else:
                # For XLSX, return URL (would implement actual XLSX generation)
                return {
                    'url': f'/admin/exports/{filename}',
                    'filename': filename,
                    'record_count': queryset.count()
                }
                
        except Exception as e:
            raise Exception(f"Error exporting commissions: {str(e)}")
    
    def get_commission_detail(self, commission_id: int) -> Dict[str, Any]:
        """Get detailed commission information"""
        try:
            commission = Commission.objects.select_related('reseller').get(id=commission_id)
            
            return {
                'id': commission.id,
                'amount': float(commission.amount),
                'status': commission.status,
                'commission_rate': float(commission.commission_rate),
                'description': getattr(commission, 'description', None) or commission.notes or commission.product_name,
                'created_at': commission.created_at.isoformat(),
                'updated_at': commission.updated_at.isoformat(),
                'reseller': {
                    'id': commission.reseller.id,
                    'name': commission.reseller.user.get_full_name() or commission.reseller.company_name or commission.reseller.user.username,
                    'company': commission.reseller.company_name
                } if commission.reseller else None
            }
            
        except Commission.DoesNotExist:
            return None
        except Exception as e:
            raise Exception(f"Error getting commission detail: {str(e)}")
    
    def get_commission_statistics(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get commission statistics"""
        try:
            queryset = Commission.objects.all()
            
            # Apply filters
            # ... (same filter logic)
            
            stats = queryset.aggregate(
                total_count=Count('id'),
                total_amount=Sum('amount'),
                pending_amount=Sum('amount', filter=Q(status='pending')),
                approved_amount=Sum('amount', filter=Q(status='approved')),
                paid_amount=Sum('amount', filter=Q(status='paid'))
            )
            
            return {
                'total_count': stats['total_count'],
                'total_amount': float(stats['total_amount'] or 0),
                'pending_amount': float(stats['pending_amount'] or 0),
                'approved_amount': float(stats['approved_amount'] or 0),
                'paid_amount': float(stats['paid_amount'] or 0)
            }
            
        except Exception as e:
            raise Exception(f"Error getting commission statistics: {str(e)}")
