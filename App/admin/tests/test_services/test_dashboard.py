"""
Tests for Admin Dashboard Service
"""
from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.cache import cache
from unittest.mock import patch, MagicMock

from ...services.dashboard_service import DashboardService
from ...repositories.dashboard_repository import DashboardRepository


class DashboardServiceTestCase(TestCase):
    """Test cases for dashboard service"""
    
    def setUp(self):
        """Set up test data"""
        self.service = DashboardService()
        cache.clear()  # Clear cache before each test
    
    @patch.object(DashboardRepository, 'get_user_metrics')
    @patch.object(DashboardRepository, 'get_business_metrics')
    @patch.object(DashboardRepository, 'get_financial_metrics')
    @patch.object(DashboardRepository, 'get_system_metrics')
    def test_get_dashboard_metrics(self, mock_system, mock_financial, 
                                  mock_business, mock_user):
        """Test getting comprehensive dashboard metrics"""
        # Mock repository responses
        mock_user.return_value = {'total_users': 100, 'new_users': 10}
        mock_business.return_value = {'total_businesses': 50, 'new_businesses': 5}
        mock_financial.return_value = {'total_revenue': 1000, 'monthly_revenue': 100}
        mock_system.return_value = {'database': 'healthy'}
        
        metrics = self.service.get_dashboard_metrics()
        
        # Verify all sections are included
        self.assertIn('users', metrics)
        self.assertIn('businesses', metrics)
        self.assertIn('financial', metrics)
        self.assertIn('system', metrics)
        self.assertIn('growth_rates', metrics)
        self.assertIn('health_score', metrics)
        
        # Verify repository methods were called
        mock_user.assert_called_once()
        mock_business.assert_called_once()
        mock_financial.assert_called_once()
        mock_system.assert_called_once()
    
    def test_get_dashboard_metrics_caching(self):
        """Test that dashboard metrics are cached"""
        with patch.object(DashboardRepository, 'get_user_metrics') as mock_user:
            mock_user.return_value = {'total_users': 100}
            
            # First call
            metrics1 = self.service.get_dashboard_metrics(period='last_7_days')
            
            # Second call - should use cache
            metrics2 = self.service.get_dashboard_metrics(period='last_7_days')
            
            # Repository should only be called once due to caching
            self.assertEqual(mock_user.call_count, 1)
            self.assertEqual(metrics1, metrics2)
    
    def test_calculate_date_range_today(self):
        """Test date range calculation for 'today'"""
        start, end = self.service._calculate_date_range('today')
        
        now = timezone.now()
        expected_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        self.assertEqual(start.date(), expected_start.date())
        self.assertEqual(start.hour, 0)
        self.assertEqual(end.date(), now.date())
    
    def test_calculate_date_range_yesterday(self):
        """Test date range calculation for 'yesterday'"""
        start, end = self.service._calculate_date_range('yesterday')
        
        yesterday = timezone.now() - timedelta(days=1)
        
        self.assertEqual(start.date(), yesterday.date())
        self.assertEqual(end.date(), yesterday.date())
        self.assertEqual(start.hour, 0)
        self.assertEqual(end.hour, 23)
    
    def test_calculate_date_range_last_7_days(self):
        """Test date range calculation for 'last_7_days'"""
        start, end = self.service._calculate_date_range('last_7_days')
        
        expected_start = timezone.now() - timedelta(days=7)
        
        self.assertAlmostEqual(
            (start - expected_start).total_seconds(), 0, delta=60
        )  # Within 1 minute
    
    def test_calculate_date_range_custom(self):
        """Test date range calculation for custom dates"""
        from_date = timezone.now() - timedelta(days=5)
        to_date = timezone.now() - timedelta(days=1)
        
        start, end = self.service._calculate_date_range('custom', from_date, to_date)
        
        self.assertEqual(start, from_date)
        self.assertEqual(end, to_date)
    
    @patch.object(DashboardRepository, 'get_recent_activities')
    def test_get_recent_activities(self, mock_activities):
        """Test getting formatted recent activities"""
        # Mock activity object
        mock_activity = MagicMock()
        mock_activity.id = 1
        mock_activity.admin_user.get_full_name.return_value = 'Admin User'
        mock_activity.admin_user.username = 'admin'
        mock_activity.action = 'CREATE'
        mock_activity.target_model = 'User'
        mock_activity.target_id = '123'
        mock_activity.created_at = timezone.now()
        mock_activity.ip_address = '127.0.0.1'
        mock_activity.description = 'Created user'
        
        mock_activities.return_value = [mock_activity]
        
        activities = self.service.get_recent_activities(limit=5)
        
        self.assertEqual(len(activities), 1)
        activity = activities[0]
        
        self.assertEqual(activity['id'], 1)
        self.assertEqual(activity['admin_user'], 'Admin User')
        self.assertEqual(activity['action'], 'CREATE')
        self.assertEqual(activity['target'], 'User')
        self.assertEqual(activity['target_id'], '123')
    
    @patch.object(DashboardRepository, 'get_system_status')
    def test_get_system_status(self, mock_status):
        """Test getting system status with health indicators"""
        mock_status.return_value = {
            'database': 'healthy',
            'cache': 'healthy',
            'storage': 'healthy',
            'external_apis': 'healthy'
        }
        
        status = self.service.get_system_status()
        
        self.assertEqual(status['overall_health'], 'healthy')
        self.assertEqual(status['healthy_services'], 4)
        self.assertEqual(status['total_services'], 4)
    
    @patch.object(DashboardRepository, 'get_system_status')
    def test_get_system_status_with_warnings(self, mock_status):
        """Test system status with some unhealthy services"""
        mock_status.return_value = {
            'database': 'healthy',
            'cache': 'error',
            'storage': 'healthy',
            'external_apis': 'warning'
        }
        
        status = self.service.get_system_status()
        
        self.assertEqual(status['overall_health'], 'warning')
        self.assertEqual(status['healthy_services'], 2)
        self.assertEqual(status['total_services'], 4)
    
    @patch.object(DashboardRepository, 'get_user_metrics')
    @patch.object(DashboardRepository, 'get_business_metrics')
    def test_get_quick_stats(self, mock_business, mock_user):
        """Test getting quick statistics"""
        # Mock today's and yesterday's metrics
        mock_user.side_effect = [
            {'new_users': 5},  # Today
            {'new_users': 3}   # Yesterday
        ]
        mock_business.side_effect = [
            {'new_businesses': 2},  # Today
            {'new_businesses': 1}   # Yesterday
        ]
        
        stats = self.service.get_quick_stats()
        
        self.assertEqual(stats['today']['new_users'], 5)
        self.assertEqual(stats['today']['new_businesses'], 2)
        self.assertEqual(stats['yesterday']['new_users'], 3)
        self.assertEqual(stats['yesterday']['new_businesses'], 1)
        
        # Check percentage changes
        self.assertIn('changes', stats)
        self.assertGreater(stats['changes']['users'], 0)  # Positive change
        self.assertGreater(stats['changes']['businesses'], 0)  # Positive change
    
    def test_calculate_percentage_change(self):
        """Test percentage change calculation"""
        # Normal case
        change = self.service._calculate_percentage_change(10, 15)
        self.assertEqual(change, 50.0)  # 50% increase
        
        # Decrease
        change = self.service._calculate_percentage_change(10, 8)
        self.assertEqual(change, -20.0)  # 20% decrease
        
        # Zero old value
        change = self.service._calculate_percentage_change(0, 5)
        self.assertEqual(change, 100.0)  # 100% when starting from zero
        
        # Zero new value
        change = self.service._calculate_percentage_change(0, 0)
        self.assertEqual(change, 0.0)
    
    @patch.object(DashboardRepository, 'get_growth_trends')
    def test_get_growth_trends(self, mock_trends):
        """Test getting growth trends with analysis"""
        mock_trends.return_value = {
            'user_growth': [
                {'date': timezone.now().date(), 'count': 10},
                {'date': timezone.now().date() - timedelta(days=1), 'count': 8},
                {'date': timezone.now().date() - timedelta(days=2), 'count': 5}
            ]
        }
        
        trends = self.service.get_growth_trends(days=3)
        
        # Should add trend analysis
        self.assertIn('user_trend', trends)
        self.assertEqual(trends['user_trend'], 'increasing')  # 5 -> 8 -> 10
    
    def test_analyze_trend_increasing(self):
        """Test trend analysis for increasing values"""
        values = [1, 2, 3, 4, 5]
        trend = self.service._analyze_trend(values)
        self.assertEqual(trend, 'increasing')
    
    def test_analyze_trend_decreasing(self):
        """Test trend analysis for decreasing values"""
        values = [5, 4, 3, 2, 1]
        trend = self.service._analyze_trend(values)
        self.assertEqual(trend, 'decreasing')
    
    def test_analyze_trend_stable(self):
        """Test trend analysis for stable values"""
        values = [5, 5, 5, 5, 5]
        trend = self.service._analyze_trend(values)
        self.assertEqual(trend, 'stable')
    
    def test_analyze_trend_single_value(self):
        """Test trend analysis with insufficient data"""
        values = [5]
        trend = self.service._analyze_trend(values)
        self.assertEqual(trend, 'stable')
    
    def test_calculate_growth_rates(self):
        """Test growth rates calculation"""
        mock_metrics = {'users': {}, 'businesses': {}}
        growth_rates = self.service._calculate_growth_rates(mock_metrics)
        
        # Should return structured growth rates
        self.assertIn('users', growth_rates)
        self.assertIn('businesses', growth_rates)
        self.assertIn('revenue', growth_rates)
        
        # Each category should have daily, weekly, monthly rates
        for category in ['users', 'businesses', 'revenue']:
            self.assertIn('daily', growth_rates[category])
            self.assertIn('weekly', growth_rates[category])
            self.assertIn('monthly', growth_rates[category])
    
    def test_calculate_health_score(self):
        """Test health score calculation"""
        # Healthy system
        metrics = {
            'system': {'database': 'healthy'}
        }
        score = self.service._calculate_health_score(metrics)
        self.assertEqual(score, 100.0)
        
        # Unhealthy system
        metrics = {
            'system': {'database': 'error'}
        }
        score = self.service._calculate_health_score(metrics)
        self.assertEqual(score, 0.0)
    
    def test_get_last_update_time(self):
        """Test getting last update time"""
        before_call = timezone.now()
        update_time = self.service.get_last_update_time()
        after_call = timezone.now()
        
        # Should return current time
        self.assertGreaterEqual(update_time, before_call)
        self.assertLessEqual(update_time, after_call)
