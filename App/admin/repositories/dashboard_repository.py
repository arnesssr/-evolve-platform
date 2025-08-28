"""
Admin Dashboard Repository
Data access layer for dashboard metrics and statistics
"""
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import connection
import os

from ...models import *  # Import all models from main app
from ..models.audit_log import AuditLog

User = get_user_model()


class DashboardRepository:
    """
    Repository for dashboard data access
    Aggregates data from multiple models for dashboard display
    """
    
    def get_user_metrics(self, start_date=None, end_date=None):
        """Get user registration and activity metrics"""
        queryset = User.objects.all()
        
        if start_date:
            queryset = queryset.filter(date_joined__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_joined__lte=end_date)
            
        return {
            'total_users': User.objects.count(),
            'new_users': queryset.count(),
            'active_users': User.objects.filter(
                last_login__gte=timezone.now() - timedelta(days=30)
            ).count(),
            'verified_users': User.objects.filter(is_verified=True).count() if hasattr(User, 'is_verified') else 0,
        }
    
    def get_business_metrics(self, start_date=None, end_date=None):
        """Get business-related metrics"""
        try:
            from App.models import Business
            
            businesses = Business.objects.all()
            if start_date:
                businesses = businesses.filter(created_at__gte=start_date)
            if end_date:
                businesses = businesses.filter(created_at__lte=end_date)
            
            return {
                'total_businesses': Business.objects.count(),
                'new_businesses': businesses.count(),
                'active_businesses': Business.objects.filter(
                    is_active=True
                ).count() if hasattr(Business, 'is_active') else 0,
                'verified_businesses': Business.objects.filter(
                    is_verified=True
                ).count() if hasattr(Business, 'is_verified') else 0,
            }
        except Exception:
            # Business model not available, return empty metrics
            return {
                'total_businesses': 0,
                'new_businesses': 0,
                'active_businesses': 0,
                'verified_businesses': 0,
            }
    
    def get_financial_metrics(self, start_date=None, end_date=None):
        """Get financial metrics from real models"""
        try:
            from App.reseller.earnings.models.invoice import Invoice
            from App.reseller.earnings.models.payout import Payout
            from App.reseller.earnings.models.base import InvoiceStatusChoices, PayoutStatusChoices
            from django.db.models import Sum, Count
            from django.utils import timezone
            from decimal import Decimal

            now = timezone.now()
            month_ago = now - timedelta(days=30)

            inv_qs = Invoice.objects.filter(status=InvoiceStatusChoices.PAID)
            if start_date:
                inv_qs = inv_qs.filter(payment_date__gte=start_date)
            if end_date:
                inv_qs = inv_qs.filter(payment_date__lte=end_date)

            total_revenue = inv_qs.aggregate(s=Sum('total_amount'))['s'] or 0
            monthly_revenue = Invoice.objects.filter(status=InvoiceStatusChoices.PAID, payment_date__gte=month_ago).aggregate(s=Sum('total_amount'))['s'] or 0

            pending_payouts = Payout.objects.filter(status__in=[PayoutStatusChoices.REQUESTED, PayoutStatusChoices.PROCESSING]).aggregate(s=Sum('amount'))['s'] or 0
            completed_tx = inv_qs.count() + Payout.objects.filter(status=PayoutStatusChoices.COMPLETED).count()
            failed_tx = Payout.objects.filter(status=PayoutStatusChoices.FAILED).count()

            return {
                'total_revenue': total_revenue,
                'monthly_revenue': monthly_revenue,
                'pending_payouts': pending_payouts,
                'completed_transactions': completed_tx,
                'failed_transactions': failed_tx,
            }
        except Exception:
            return {
                'total_revenue': 0,
                'monthly_revenue': 0,
                'pending_payouts': 0,
                'completed_transactions': 0,
                'failed_transactions': 0,
            }
    
    def get_system_metrics(self):
        """Get system health and performance metrics, DB-vendor aware"""
        vendor = getattr(connection, 'vendor', '')
        db_size = 0
        table_stats = []

        if vendor == 'postgresql':
            with connection.cursor() as cursor:
                # Database size in bytes
                cursor.execute("SELECT pg_database_size(current_database())")
                db_size = cursor.fetchone()[0] if cursor.rowcount > 0 else 0

                # Top tables by total write operations
                cursor.execute(
                    """
                    SELECT schemaname, relname AS tablename,
                           n_tup_ins + n_tup_upd + n_tup_del AS total_operations
                    FROM pg_stat_user_tables
                    ORDER BY total_operations DESC
                    LIMIT 10
                    """
                )
                table_stats = cursor.fetchall()
        else:
            # Fallback for SQLite and other engines
            # Attempt to compute DB size for SQLite from file size
            engine_name = connection.settings_dict.get('ENGINE', '')
            if 'sqlite' in engine_name:
                db_path = connection.settings_dict.get('NAME')
                if db_path and os.path.exists(db_path):
                    try:
                        db_size = os.path.getsize(db_path)
                    except OSError:
                        db_size = 0
            # Approximate "table activity" by row counts per table
            try:
                table_names = connection.introspection.table_names()
                counts = []
                with connection.cursor() as cursor:
                    for t in table_names:
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM {connection.ops.quote_name(t)}")
                            cnt = cursor.fetchone()[0]
                            counts.append((t, cnt))
                        except Exception:
                            # Skip tables we cannot count
                            continue
                counts.sort(key=lambda x: x[1], reverse=True)
                # Normalize format to (schemaname_or_none, tablename, metric)
                table_stats = [(None, name, count) for name, count in counts[:10]]
            except Exception:
                table_stats = []

        return {
            'database_size': db_size,
            'table_operations': table_stats,
            'active_connections': connection.queries.__len__(),
        }
    
    def get_recent_activities(self, limit=20):
        """Get recent admin audit log activities"""
        return AuditLog.objects.select_related(
            'actor'
        ).order_by('-created_at')[:limit]
    
    def get_top_performing_items(self, item_type='users', limit=10):
        """Get top performing items by type"""
        if item_type == 'users':
            return User.objects.filter(
                is_active=True
            ).order_by('-date_joined')[:limit]
        
        elif item_type == 'businesses':
            try:
                from ...business.models import Business
                return Business.objects.filter(
                    is_active=True
                ).order_by('-created_at')[:limit]
            except ImportError:
                return []
        
        return []
    
    def get_growth_trends(self, days=30):
        """Get growth trends over specified days"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        from App.reseller.earnings.models.invoice import Invoice
        from App.reseller.earnings.models.base import InvoiceStatusChoices
        try:
            from App.models import Business
        except Exception:
            Business = None

        user_growth = []
        business_growth = []
        revenue_growth = []

        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            # Users
            user_count = User.objects.filter(date_joined__date=current_date).count()
            user_growth.append({'date': current_date, 'count': user_count})
            # Businesses
            if Business:
                biz_count = Business.objects.filter(created_at__date=current_date).count()
            else:
                biz_count = 0
            business_growth.append({'date': current_date, 'count': biz_count})
            # Revenue
            try:
                # Handle both DateField and DateTimeField for payment_date
                from django.db.models import DateTimeField
                payment_field = Invoice._meta.get_field('payment_date')
                if isinstance(payment_field, DateTimeField):
                    from datetime import datetime
                    from django.utils import timezone as dj_tz
                    tz = dj_tz.get_current_timezone()
                    start_dt = dj_tz.make_aware(datetime.combine(current_date, datetime.min.time()), tz) if dj_tz.is_naive(datetime.combine(current_date, datetime.min.time())) else datetime.combine(current_date, datetime.min.time())
                    end_dt = dj_tz.make_aware(datetime.combine(next_date, datetime.min.time()), tz) if dj_tz.is_naive(datetime.combine(next_date, datetime.min.time())) else datetime.combine(next_date, datetime.min.time())
                    rev_qs = Invoice.objects.filter(status=InvoiceStatusChoices.PAID, payment_date__gte=start_dt, payment_date__lt=end_dt)
                else:
                    # DateField: match exact day
                    rev_qs = Invoice.objects.filter(status=InvoiceStatusChoices.PAID, payment_date=current_date)
                rev_sum = rev_qs.aggregate(s=Sum('total_amount'))['s'] or 0
            except Exception:
                rev_sum = 0
            try:
                rev_count = int(rev_sum)
            except Exception:
                # Fallback if non-numeric
                rev_count = 0
            revenue_growth.append({'date': current_date, 'count': rev_count})
            current_date = next_date
        
        return {
            'user_growth': user_growth,
            'business_growth': business_growth,
            'revenue_growth': revenue_growth,
        }
    
    def get_system_status(self):
        """Get current system status indicators"""
        try:
            # Check database connectivity
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = 'healthy'
        except Exception:
            db_status = 'error'
        
        return {
            'database': db_status,
            'cache': 'healthy',  # Would check actual cache
            'storage': 'healthy',  # Would check storage
            'external_apis': 'healthy',  # Would check external services
            'last_backup': timezone.now() - timedelta(hours=2),  # Placeholder
        }
