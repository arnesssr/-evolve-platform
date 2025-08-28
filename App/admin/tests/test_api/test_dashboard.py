"""
Tests for Admin Dashboard API Views
"""
import json
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from unittest.mock import patch, MagicMock

from ...api.v1.views.dashboard import (
    dashboard_metrics_api,
    recent_activities_api,
    system_status_api,
    quick_stats_api,
    growth_trends_api,
    dashboard_summary_api,
    refresh_dashboard_cache
)
from ...services.dashboard_service import DashboardService

User = get_user_model()


class DashboardAPITestCase(TestCase):
    """Test cases for dashboard API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123'
        )
        
        cache.clear()
    
    def test_dashboard_metrics_api_requires_authentication(self):
        """Test that API requires authentication"""
        response = self.client.get('/admin/api/v1/dashboard/metrics/')
        self.assertEqual(response.status_code, 401)  # Unauthorized
    
    def test_dashboard_metrics_api_requires_staff(self):
        """Test that API requires staff privileges"""
        self.client.force_login(self.regular_user)
        response = self.client.get('/admin/api/v1/dashboard/metrics/')
        self.assertIn(response.status_code, [302, 403])  # Redirect or forbidden
    
    @patch.object(DashboardService, 'get_dashboard_metrics')
    def test_dashboard_metrics_api_success(self, mock_metrics):
        """Test successful dashboard metrics API call"""
        mock_metrics.return_value = {
            'users': {'total_users': 100, 'new_users': 10},
            'businesses': {'total_businesses': 50, 'new_businesses': 5},
            'financial': {'total_revenue': 1000, 'monthly_revenue': 100},
            'system': {'database_size': 1024, 'active_connections': 5},
            'period': 'last_7_days',
            'date_range': {
                'start': timezone.now() - timedelta(days=7),
                'end': timezone.now()
            },
            'growth_rates': {
                'users': {'daily': 0.05, 'weekly': 0.15, 'monthly': 0.25},
                'businesses': {'daily': 0.02, 'weekly': 0.08, 'monthly': 0.12},
                'revenue': {'daily': 0.03, 'weekly': 0.10, 'monthly': 0.20}
            },
            'health_score': 95.5
        }
        
        self.client.force_login(self.admin_user)
        response = self.client.get('/admin/api/v1/dashboard/metrics/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertIn('users', data)
        self.assertIn('businesses', data)
        self.assertIn('financial', data)
        self.assertIn('system', data)
        self.assertIn('growth_rates', data)
        self.assertIn('health_score', data)
    
    def test_dashboard_metrics_api_with_filters(self):
        """Test dashboard metrics API with filter parameters"""
        with patch.object(DashboardService, 'get_dashboard_metrics') as mock_metrics:
            mock_metrics.return_value = {'users': {'total_users': 50}}
            
            self.client.force_login(self.admin_user)
            response = self.client.get('/admin/api/v1/dashboard/metrics/', {
                'period': 'last_30_days',
                'metric_type': 'users'
            })
            
            self.assertEqual(response.status_code, 200)
            
            # Verify service was called with correct parameters
            mock_metrics.assert_called_once_with(
                period='last_30_days',
                date_from=None,
                date_to=None
            )
    
    def test_dashboard_metrics_api_invalid_filters(self):
        """Test dashboard metrics API with invalid filters"""
        self.client.force_login(self.admin_user)
        response = self.client.get('/admin/api/v1/dashboard/metrics/', {
            'period': 'invalid_period',
            'refresh_interval': 5  # Too low
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('details', data)
    
    @patch.object(DashboardService, 'get_recent_activities')
    def test_recent_activities_api(self, mock_activities):
        """Test recent activities API endpoint"""
        mock_activities.return_value = [
            {
                'id': 1,
                'admin_user': 'Admin User',
                'action': 'CREATE',
                'target': 'User',
                'target_id': '123',
                'timestamp': timezone.now(),
                'ip_address': '127.0.0.1',
                'description': 'Created user'
            }
        ]
        
        self.client.force_login(self.admin_user)
        response = self.client.get('/admin/api/v1/dashboard/recent-activities/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['admin_user'], 'Admin User')
        self.assertEqual(data[0]['action'], 'CREATE')
    
    def test_recent_activities_api_with_limit(self):
        """Test recent activities API with limit parameter"""
        with patch.object(DashboardService, 'get_recent_activities') as mock_activities:
            mock_activities.return_value = []
            
            self.client.force_login(self.admin_user)
            response = self.client.get('/admin/api/v1/dashboard/recent-activities/', {
                'limit': 20
            })
            
            self.assertEqual(response.status_code, 200)
            mock_activities.assert_called_once_with(limit=20)
    
    def test_recent_activities_api_limit_cap(self):
        """Test that activities API caps limit at 50"""
        with patch.object(DashboardService, 'get_recent_activities') as mock_activities:
            mock_activities.return_value = []
            
            self.client.force_login(self.admin_user)
            response = self.client.get('/admin/api/v1/dashboard/recent-activities/', {
                'limit': 100  # Should be capped at 50
            })
            
            self.assertEqual(response.status_code, 200)
            mock_activities.assert_called_once_with(limit=50)
    
    @patch.object(DashboardService, 'get_system_status')
    def test_system_status_api(self, mock_status):
        """Test system status API endpoint"""
        mock_status.return_value = {
            'database': 'healthy',
            'cache': 'healthy',
            'storage': 'healthy',
            'external_apis': 'healthy',
            'overall_health': 'healthy',
            'healthy_services': 4,
            'total_services': 4,
            'last_backup': timezone.now() - timedelta(hours=2)
        }
        
        self.client.force_login(self.admin_user)
        response = self.client.get('/admin/api/v1/dashboard/system-status/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['database'], 'healthy')
        self.assertEqual(data['overall_health'], 'healthy')
        self.assertEqual(data['healthy_services'], 4)
    
    @patch.object(DashboardService, 'get_quick_stats')
    def test_quick_stats_api(self, mock_stats):
        """Test quick stats API endpoint"""
        mock_stats.return_value = {
            'today': {'new_users': 5, 'new_businesses': 2},
            'yesterday': {'new_users': 3, 'new_businesses': 1},
            'changes': {'users': 66.67, 'businesses': 100.0}
        }
        
        self.client.force_login(self.admin_user)
        response = self.client.get('/admin/api/v1/dashboard/quick-stats/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['today']['new_users'], 5)
        self.assertEqual(data['changes']['users'], 66.67)
    
    @patch.object(DashboardService, 'get_growth_trends')
    def test_growth_trends_api(self, mock_trends):
        """Test growth trends API endpoint"""
        mock_trends.return_value = {
            'user_growth': [
                {'date': timezone.now().date(), 'count': 10},
                {'date': timezone.now().date() - timedelta(days=1), 'count': 8}
            ],
            'business_growth': [],
            'revenue_growth': [],
            'user_trend': 'increasing'
        }
        
        self.client.force_login(self.admin_user)
        response = self.client.get('/admin/api/v1/dashboard/growth-trends/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(len(data['user_growth']), 2)
        self.assertEqual(data['user_trend'], 'increasing')
    
    def test_growth_trends_api_with_days_parameter(self):
        """Test growth trends API with days parameter"""
        with patch.object(DashboardService, 'get_growth_trends') as mock_trends:
            mock_trends.return_value = {'user_growth': []}
            
            self.client.force_login(self.admin_user)
            response = self.client.get('/admin/api/v1/dashboard/growth-trends/', {
                'days': 60
            })
            
            self.assertEqual(response.status_code, 200)
            mock_trends.assert_called_once_with(days=60)
    
    def test_growth_trends_api_days_cap(self):
        """Test that growth trends API caps days at 365"""
        with patch.object(DashboardService, 'get_growth_trends') as mock_trends:
            mock_trends.return_value = {'user_growth': []}
            
            self.client.force_login(self.admin_user)
            response = self.client.get('/admin/api/v1/dashboard/growth-trends/', {
                'days': 500  # Should be capped at 365
            })
            
            self.assertEqual(response.status_code, 200)
            mock_trends.assert_called_once_with(days=365)
    
    @patch.object(DashboardService, 'get_dashboard_metrics')
    @patch.object(DashboardService, 'get_quick_stats')
    @patch.object(DashboardService, 'get_system_status')
    @patch.object(DashboardService, 'get_recent_activities')
    @patch.object(DashboardService, 'get_last_update_time')
    def test_dashboard_summary_api(self, mock_update_time, mock_activities,
                                  mock_status, mock_stats, mock_metrics):
        """Test comprehensive dashboard summary API"""
        # Mock all service responses
        mock_metrics.return_value = {'users': {'total_users': 100}}
        mock_stats.return_value = {'today': {'new_users': 5}}
        mock_status.return_value = {'database': 'healthy'}
        mock_activities.return_value = [{'id': 1, 'action': 'CREATE'}]
        mock_update_time.return_value = timezone.now()
        
        self.client.force_login(self.admin_user)
        response = self.client.get('/admin/api/v1/dashboard/summary/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('metrics', data)
        self.assertIn('quick_stats', data)
        self.assertIn('system_status', data)
        self.assertIn('recent_activities', data)
        self.assertIn('last_updated', data)
        
        # Verify service methods were called
        mock_metrics.assert_called_once()
        mock_stats.assert_called_once()
        mock_status.assert_called_once()
        mock_activities.assert_called_once_with(limit=5)
        mock_update_time.assert_called_once()
    
    @patch('django.core.cache.cache.delete_pattern')
    def test_refresh_dashboard_cache_api(self, mock_delete_pattern):
        """Test dashboard cache refresh API"""
        self.client.force_login(self.admin_user)
        response = self.client.post('/admin/api/v1/dashboard/refresh-cache/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('message', data)
        self.assertIn('refreshed successfully', data['message'])
        
        # Verify cache deletion was attempted
        self.assertTrue(mock_delete_pattern.called)
    
    def test_api_error_handling(self):
        """Test API error handling when service throws exception"""
        with patch.object(DashboardService, 'get_dashboard_metrics') as mock_metrics:
            mock_metrics.side_effect = Exception("Service error")
            
            self.client.force_login(self.admin_user)
            response = self.client.get('/admin/api/v1/dashboard/metrics/')
            
            self.assertEqual(response.status_code, 500)
            
            data = json.loads(response.content)
            self.assertIn('error', data)
            self.assertIn('details', data)
    
    def test_api_content_type(self):
        """Test that all API endpoints return JSON content type"""
        endpoints = [
            '/admin/api/v1/dashboard/metrics/',
            '/admin/api/v1/dashboard/recent-activities/',
            '/admin/api/v1/dashboard/system-status/',
            '/admin/api/v1/dashboard/quick-stats/',
            '/admin/api/v1/dashboard/growth-trends/',
            '/admin/api/v1/dashboard/summary/',
        ]
        
        # Mock all service methods to avoid actual calls
        with patch.object(DashboardService, 'get_dashboard_metrics'), \
             patch.object(DashboardService, 'get_recent_activities'), \
             patch.object(DashboardService, 'get_system_status'), \
             patch.object(DashboardService, 'get_quick_stats'), \
             patch.object(DashboardService, 'get_growth_trends'), \
             patch.object(DashboardService, 'get_last_update_time'):
            
            self.client.force_login(self.admin_user)
            
            for endpoint in endpoints:
                response = self.client.get(endpoint)
                self.assertEqual(
                    response['Content-Type'], 
                    'application/json',
                    f"Endpoint {endpoint} should return JSON"
                )
    
    def test_api_authentication_methods(self):
        """Test different authentication methods work with API"""
        with patch.object(DashboardService, 'get_dashboard_metrics') as mock_metrics:
            mock_metrics.return_value = {'users': {'total_users': 100}}
            
            # Test with force_login (session auth)
            self.client.force_login(self.admin_user)
            response = self.client.get('/admin/api/v1/dashboard/metrics/')
            self.assertEqual(response.status_code, 200)
            
            # Test with login (form auth)
            self.client.logout()
            login_success = self.client.login(username='admin', password='testpass123')
            self.assertTrue(login_success)
            
            response = self.client.get('/admin/api/v1/dashboard/metrics/')
            self.assertEqual(response.status_code, 200)
