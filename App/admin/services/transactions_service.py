"""
Admin Transactions Service
Provides unified transaction management, analytics, and reconciliation functionality.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.db import transaction
from django.contrib.auth import get_user_model
import statistics

from App.admin.repositories.transactions_repository import TransactionsRepository

User = get_user_model()


class TransactionsService:
    """Admin service for transaction management and analytics"""
    
    def __init__(self):
        self.repository = TransactionsRepository()
    
    def get_transactions_list(self, page: int = 1, page_size: int = 25, 
                            filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get paginated list of unified transactions with filtering"""
        try:
            return self.repository.get_transactions_list(page, page_size, filters or {})
        except Exception as e:
            raise Exception(f"Error getting transactions list: {str(e)}")
    
    def get_transaction_metrics(self, start_date: datetime, end_date: datetime, 
                               interval: str = 'daily') -> Dict[str, Any]:
        """
        Get transaction metrics and analytics
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            interval: Time interval ('daily', 'weekly', 'monthly')
            
        Returns:
            Dictionary containing transaction metrics and chart data
        """
        try:
            # Get volume data over time
            volume_data = self.repository.get_volume_by_interval(start_date, end_date, interval)
            
            # Get type breakdown
            type_breakdown = self.repository.get_type_breakdown(start_date, end_date)
            
            # Get method breakdown
            method_breakdown = self.repository.get_method_breakdown(start_date, end_date)
            
            # Calculate summary statistics
            total_volume = sum(
                float(item['incoming']) + float(item['outgoing']) + float(item['internal']) 
                for item in volume_data
            )
            
            transaction_count = self.repository.get_transaction_count(start_date, end_date)
            avg_transaction = total_volume / transaction_count if transaction_count > 0 else 0
            
            # Calculate growth rate (comparing to previous period)
            period_length = end_date - start_date
            previous_start = start_date - period_length
            previous_end = start_date
            previous_count = self.repository.get_transaction_count(previous_start, previous_end)
            
            growth_rate = 0
            if previous_count > 0:
                growth_rate = ((transaction_count - previous_count) / previous_count) * 100
            
            return {
                'volume_data': volume_data,
                'type_breakdown': type_breakdown,
                'method_breakdown': method_breakdown,
                'summary': {
                    'total_volume': float(total_volume),
                    'transaction_count': transaction_count,
                    'avg_transaction': float(avg_transaction),
                    'growth_rate': float(growth_rate)
                }
            }
            
        except Exception as e:
            raise Exception(f"Error getting transaction metrics: {str(e)}")
    
    def mark_reconciled(self, transaction_ids: List[int], reconciliation_date: str,
                       reference: str, notes: str, user: User) -> Dict[str, Any]:
        """Mark transactions as reconciled"""
        try:
            processed_count = 0
            failed_count = 0
            
            with transaction.atomic():
                for transaction_id in transaction_ids:
                    try:
                        self.repository.mark_transaction_reconciled(
                            transaction_id, reconciliation_date, reference, notes, user
                        )
                        processed_count += 1
                    except Exception:
                        failed_count += 1
            
            return {
                'processed_count': processed_count,
                'failed_count': failed_count
            }
            
        except Exception as e:
            raise Exception(f"Error marking transactions reconciled: {str(e)}")
    
    def mark_disputed(self, transaction_ids: List[int], reason: str, user: User) -> Dict[str, Any]:
        """Mark transactions as disputed"""
        try:
            processed_count = 0
            failed_count = 0
            
            with transaction.atomic():
                for transaction_id in transaction_ids:
                    try:
                        self.repository.mark_transaction_disputed(transaction_id, reason, user)
                        processed_count += 1
                    except Exception:
                        failed_count += 1
            
            return {
                'processed_count': processed_count,
                'failed_count': failed_count
            }
            
        except Exception as e:
            raise Exception(f"Error marking transactions disputed: {str(e)}")
    
    def auto_reconcile(self, start_date: str, end_date: str, tolerance: float, 
                      user: User) -> Dict[str, Any]:
        """Automatically reconcile transactions within tolerance"""
        try:
            return self.repository.auto_reconcile_transactions(
                start_date, end_date, tolerance, user
            )
        except Exception as e:
            raise Exception(f"Error auto-reconciling transactions: {str(e)}")
    
    def export_transactions(self, filters: Dict[str, Any] = None, format: str = 'csv',
                           fields: List[str] = None, include_summary: bool = True) -> Dict[str, Any]:
        """Export transactions to specified format"""
        try:
            return self.repository.export_transactions(
                filters=filters or {},
                format=format,
                fields=fields or [],
                include_summary=include_summary
            )
        except Exception as e:
            raise Exception(f"Error exporting transactions: {str(e)}")
    
    def get_transaction_detail(self, transaction_id: int, 
                              include_related: bool = False) -> Optional[Dict[str, Any]]:
        """Get detailed transaction information"""
        try:
            return self.repository.get_transaction_detail(transaction_id, include_related)
        except Exception as e:
            raise Exception(f"Error getting transaction detail: {str(e)}")
    
    def get_cash_flow_analysis(self, start_date: datetime, end_date: datetime,
                              interval: str = 'weekly', forecast_periods: int = 4) -> Dict[str, Any]:
        """
        Get cash flow analysis with historical data and forecasting
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            interval: Time interval ('daily', 'weekly', 'monthly')
            forecast_periods: Number of future periods to forecast
            
        Returns:
            Dictionary containing cash flow analysis
        """
        try:
            # Get historical cash flow data
            historical = self.repository.get_cash_flow_by_interval(start_date, end_date, interval)
            
            # Calculate net flow for each period
            for period in historical:
                period['net_flow'] = float(period['inflow']) - float(period['outflow'])
            
            # Generate forecast if requested
            forecast = []
            if forecast_periods > 0 and len(historical) >= 2:
                # Simple moving average forecast
                recent_flows = [period['net_flow'] for period in historical[-3:]]
                avg_flow = sum(recent_flows) / len(recent_flows)
                
                for i in range(forecast_periods):
                    if interval == 'weekly':
                        forecast_date = end_date + timedelta(weeks=i + 1)
                    elif interval == 'monthly':
                        forecast_date = end_date + timedelta(days=30 * (i + 1))
                    else:  # daily
                        forecast_date = end_date + timedelta(days=i + 1)
                    
                    forecast.append({
                        'period': forecast_date.strftime('%Y-%m-%d'),
                        'net_flow': avg_flow * (0.95 ** i),  # Slight decay in forecast
                        'confidence': max(0.8 - (i * 0.1), 0.4)
                    })
            
            # Calculate summary statistics
            net_flows = [period['net_flow'] for period in historical]
            inflows = [float(period['inflow']) for period in historical]
            outflows = [float(period['outflow']) for period in historical]
            
            avg_inflow = statistics.mean(inflows) if inflows else 0
            avg_outflow = statistics.mean(outflows) if outflows else 0
            avg_net_flow = statistics.mean(net_flows) if net_flows else 0
            
            # Determine trend
            if len(net_flows) >= 3:
                recent_trend = net_flows[-1] - net_flows[-3]
                if recent_trend > avg_net_flow * 0.1:
                    trend = 'improving'
                elif recent_trend < -avg_net_flow * 0.1:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            # Calculate volatility (standard deviation)
            volatility = statistics.stdev(net_flows) if len(net_flows) > 1 else 0
            
            return {
                'historical': historical,
                'forecast': forecast,
                'summary': {
                    'avg_inflow': float(avg_inflow),
                    'avg_outflow': float(avg_outflow),
                    'avg_net_flow': float(avg_net_flow),
                    'trend': trend,
                    'volatility': float(volatility)
                }
            }
            
        except Exception as e:
            raise Exception(f"Error getting cash flow analysis: {str(e)}")
    
    def get_reconciliation_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get reconciliation report for the specified period"""
        try:
            return self.repository.get_reconciliation_report(start_date, end_date)
        except Exception as e:
            raise Exception(f"Error getting reconciliation report: {str(e)}")
    
    def get_transaction_summary(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get transaction summary statistics"""
        try:
            return self.repository.get_transaction_summary(filters or {})
        except Exception as e:
            raise Exception(f"Error getting transaction summary: {str(e)}")
