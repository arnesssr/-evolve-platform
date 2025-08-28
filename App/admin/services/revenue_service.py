"""
Admin Revenue Service
Provides revenue metrics, trends analysis, and forecasting functionality.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import statistics

from App.admin.repositories.revenue_repository import RevenueRepository


class RevenueService:
    """Service for revenue-related operations and analytics"""
    
    def __init__(self):
        self.repository = RevenueRepository()
    
    def get_revenue_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Get comprehensive revenue metrics for the specified period
        
        Args:
            start_date: Start date for the period
            end_date: End date for the period
            
        Returns:
            Dictionary containing revenue metrics
        """
        try:
            # Get raw metrics from repository
            metrics = self.repository.get_revenue_metrics(start_date, end_date)
            
            # Calculate derived metrics using Decimal to avoid float issues
            total_revenue = Decimal(metrics.get('total_revenue', 0) or 0)
            total_days = (end_date - start_date).days or 1
            
            # Monthly Recurring Revenue (rough calculation)
            if total_days < 365:
                mrr = total_revenue * (Decimal(30) / Decimal(total_days))
            else:
                mrr = total_revenue / Decimal(12)
            
            # Annual Recurring Revenue
            arr = mrr * Decimal(12)
            
            # Growth rate (comparing to previous period)
            previous_start = start_date - (end_date - start_date)
            previous_end = start_date
            previous_metrics = self.repository.get_revenue_metrics(previous_start, previous_end)
            previous_revenue = Decimal(previous_metrics.get('total_revenue', 0) or 0)
            
            growth_rate = Decimal(0)
            if previous_revenue > 0:
                growth_rate = ((total_revenue - previous_revenue) / previous_revenue) * Decimal(100)
            
            return {
                'total_revenue': float(total_revenue),
                'mrr': float(mrr),
                'arr': float(arr),
                'growth_rate': float(growth_rate),
                'pending_commissions': float(metrics.get('pending_commissions', 0) or 0),
                'processed_payouts': float(metrics.get('processed_payouts', 0) or 0),
                'invoice_count': metrics.get('invoice_count', 0) or 0,
                'avg_invoice_value': float(metrics.get('avg_invoice_value', 0) or 0),
                'commission_rate': float(metrics.get('avg_commission_rate', 0) or 0),
                'period_days': total_days,
                'daily_average': float(total_revenue / Decimal(total_days)) if total_days > 0 else 0
            }
            
        except Exception as e:
            raise Exception(f"Error calculating revenue metrics: {str(e)}")
    
    def get_source_breakdown(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Get revenue breakdown by source (resellers, direct sales, etc.)
        
        Args:
            start_date: Start date for the period
            end_date: End date for the period
            
        Returns:
            Dictionary containing source breakdown data
        """
        try:
            sources = self.repository.get_revenue_by_source(start_date, end_date)
            
            # Calculate percentages
            total = sum(source['amount'] for source in sources)
            
            for source in sources:
                source['percentage'] = (source['amount'] / total * 100) if total > 0 else 0
                source['amount'] = float(source['amount'])
            
            return {
                'sources': sources,
                'total_amount': float(total),
                'source_count': len(sources)
            }
            
        except Exception as e:
            raise Exception(f"Error getting revenue source breakdown: {str(e)}")
    
    def get_revenue_trends(self, start_date: datetime, end_date: datetime, 
                          interval: str = 'monthly') -> Dict[str, Any]:
        """
        Get revenue trends over time
        
        Args:
            start_date: Start date for the period
            end_date: End date for the period
            interval: Time interval ('daily', 'weekly', 'monthly')
            
        Returns:
            Dictionary containing trend data
        """
        try:
            trends = self.repository.get_revenue_trends(start_date, end_date, interval)
            
            # Calculate additional metrics
            revenue_values = [trend['revenue'] for trend in trends]
            commission_values = [trend['commissions'] for trend in trends]
            
            avg_revenue = statistics.mean(revenue_values) if revenue_values else 0
            
            # Determine growth trend
            growth_trend = 'stable'
            if len(revenue_values) >= 2:
                # Simple trend calculation based on first and last values
                if revenue_values[-1] > revenue_values[0] * 1.05:  # 5% threshold
                    growth_trend = 'growing'
                elif revenue_values[-1] < revenue_values[0] * 0.95:  # 5% threshold
                    growth_trend = 'declining'
            
            # Convert Decimal to float for JSON serialization
            for trend in trends:
                trend['revenue'] = float(trend['revenue'])
                trend['commissions'] = float(trend['commissions'])
            
            return {
                'trends': trends,
                'avg_revenue': float(avg_revenue),
                'growth_trend': growth_trend,
                'total_periods': len(trends),
                'interval': interval
            }
            
        except Exception as e:
            raise Exception(f"Error calculating revenue trends: {str(e)}")
    
    def get_revenue_forecast(self, periods: int, method: str = 'moving_average') -> Dict[str, Any]:
        """
        Generate revenue forecast
        
        Args:
            periods: Number of periods to forecast
            method: Forecasting method ('moving_average', 'linear_trend')
            
        Returns:
            Dictionary containing forecast data
        """
        try:
            # Get historical data (last 12 periods for forecasting)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            historical = self.repository.get_revenue_trends(start_date, end_date, 'monthly')
            
            if not historical:
                return {
                    'forecast': [],
                    'historical': [],
                    'confidence': 0.0,
                    'method': method
                }
            
            forecast = []
            
            if method == 'moving_average':
                # Simple moving average forecast
                window_size = min(3, len(historical))
                if len(historical) >= window_size:
                    recent_values = [float(h['revenue']) for h in historical[-window_size:]]
                    avg_value = sum(recent_values) / len(recent_values)
                    
                    for i in range(periods):
                        forecast_date = end_date + timedelta(days=30 * (i + 1))
                        forecast.append({
                            'period': forecast_date.strftime('%Y-%m'),
                            'amount': avg_value,
                            'confidence': max(0.8 - (i * 0.1), 0.3)  # Decreasing confidence
                        })
            
            elif method == 'linear_trend':
                # Simple linear trend forecast
                if len(historical) >= 2:
                    values = [float(h['revenue']) for h in historical]
                    n = len(values)
                    
                    # Calculate trend line
                    x_vals = list(range(n))
                    sum_x = sum(x_vals)
                    sum_y = sum(values)
                    sum_xy = sum(x * y for x, y in zip(x_vals, values))
                    sum_x2 = sum(x * x for x in x_vals)
                    
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                    intercept = (sum_y - slope * sum_x) / n
                    
                    for i in range(periods):
                        next_x = n + i
                        predicted_value = max(0, slope * next_x + intercept)
                        forecast_date = end_date + timedelta(days=30 * (i + 1))
                        
                        forecast.append({
                            'period': forecast_date.strftime('%Y-%m'),
                            'amount': predicted_value,
                            'confidence': max(0.9 - (i * 0.1), 0.4)  # Decreasing confidence
                        })
            
            # Convert historical data for consistency
            for h in historical:
                h['revenue'] = float(h['revenue'])
                h['commissions'] = float(h['commissions'])
            
            # Calculate overall confidence based on data quality
            base_confidence = 0.8 if len(historical) >= 6 else 0.6
            
            return {
                'forecast': forecast,
                'historical': historical,
                'confidence': base_confidence,
                'method': method
            }
            
        except Exception as e:
            raise Exception(f"Error generating revenue forecast: {str(e)}")
    
    def get_revenue_comparison(self, current_start: datetime, current_end: datetime,
                              comparison_start: datetime, comparison_end: datetime) -> Dict[str, Any]:
        """
        Compare revenue between two periods
        
        Args:
            current_start: Start date for current period
            current_end: End date for current period
            comparison_start: Start date for comparison period
            comparison_end: End date for comparison period
            
        Returns:
            Dictionary containing comparison data
        """
        try:
            current_metrics = self.get_revenue_metrics(current_start, current_end)
            comparison_metrics = self.get_revenue_metrics(comparison_start, comparison_end)
            
            # Calculate changes
            revenue_change = current_metrics['total_revenue'] - comparison_metrics['total_revenue']
            revenue_change_percent = 0
            if comparison_metrics['total_revenue'] > 0:
                revenue_change_percent = (revenue_change / comparison_metrics['total_revenue']) * 100
            
            commission_change = current_metrics['pending_commissions'] - comparison_metrics['pending_commissions']
            commission_change_percent = 0
            if comparison_metrics['pending_commissions'] > 0:
                commission_change_percent = (commission_change / comparison_metrics['pending_commissions']) * 100
            
            return {
                'current': current_metrics,
                'comparison': comparison_metrics,
                'changes': {
                    'revenue_change': float(revenue_change),
                    'revenue_change_percent': float(revenue_change_percent),
                    'commission_change': float(commission_change),
                    'commission_change_percent': float(commission_change_percent),
                },
                'performance': {
                    'is_growing': revenue_change > 0,
                    'growth_strength': 'strong' if abs(revenue_change_percent) > 20 else 
                                    'moderate' if abs(revenue_change_percent) > 5 else 'weak'
                }
            }
            
        except Exception as e:
            raise Exception(f"Error comparing revenue periods: {str(e)}")
    
    def get_top_revenue_sources(self, start_date: datetime, end_date: datetime, 
                               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top revenue sources (resellers, products, etc.)
        
        Args:
            start_date: Start date for the period
            end_date: End date for the period
            limit: Maximum number of sources to return
            
        Returns:
            List of top revenue sources
        """
        try:
            sources = self.repository.get_top_revenue_sources(start_date, end_date, limit)
            
            # Calculate rankings and percentages
            total_revenue = sum(float(source['revenue']) for source in sources)
            
            for i, source in enumerate(sources, 1):
                source['rank'] = i
                source['revenue'] = float(source['revenue'])
                source['percentage'] = (source['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            
            return sources
            
        except Exception as e:
            raise Exception(f"Error getting top revenue sources: {str(e)}")
