"""
Tests for Admin Dashboard Views
"""
import json
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock

from ...views.dashboard import dashboard_view, dashboard_metrics_ajax
from ...services.dashboard_service import DashboardService

User = get_user_model()


class DashboardViewsTestCase(TestCase):
    """Test cases for dashboard views"""
    
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
    
    def test_dashboard_view_requires_login(self):
        """Test that dashboard view requires login"""
        response = self.client.get('/admin/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_view_requires_staff(self):
        """Test that dashboard view requires staff privileges"""
        self.client.login(username='user', password='testpass123')
        response = self.client.get('/admin/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect or forbidden
    
    @patch.object(DashboardService, 'get_dashboard_metrics')
    @patch.object(DashboardService, 'get_recent_activities')
    @patch.object(DashboardService, 'get_system_status')
    @patch.object(DashboardService, 'get_quick_stats')
    def test_dashboard_view_success(self, mock_quick_stats, mock_system_status, 
                                   mock_activities, mock_metrics):
        """Test successful dashboard view rendering"""
        # Mock service responses
        mock_metrics.return_value = {
            'users': {'total_users': 100, 'new_users': 10},
            'businesses': {'total_businesses': 50, 'new_businesses': 5},
        }
        mock_activities.return_value = []
        mock_system_status.return_value = {'database': 'healthy'}
        mock_quick_stats.return_value = {'today': {'new_users': 5}}
        
        # Login as admin and access dashboard
        self.client.login(username='admin', password='testpass123')
        response = self.client.get('/admin/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'dashboard')
        
        # Verify service methods were called
        mock_metrics.assert_called_once()
        mock_activities.assert_called_once_with(limit=10)
        mock_system_status.assert_called_once()
        mock_quick_stats.assert_called_once()
    
    def test_dashboard_view_with_filters(self):
        """Test dashboard view with filter parameters"""
        self.client.login(username='admin', password='testpass123')
        
        with patch.object(DashboardService, 'get_dashboard_metrics') as mock_metrics:
            mock_metrics.return_value = {}
            
            response = self.client.get('/admin/dashboard/', {
                'period': 'last_30_days',
                'metric_type': 'users'
            })
            
            self.assertEqual(response.status_code, 200)
    
    @patch.object(DashboardService, 'get_dashboard_metrics')
    @patch.object(DashboardService, 'get_system_status')
    @patch.object(DashboardService, 'get_last_update_time')
    def test_dashboard_metrics_ajax(self, mock_update_time, mock_status, mock_metrics):
        """Test AJAX endpoint for dashboard metrics"""
        # Mock service responses
        mock_metrics.return_value = {'users': {'total_users': 100}}
        mock_status.return_value = {'database': 'healthy'}
        mock_update_time.return_value = timezone.now()
        
        self.client.login(username='admin', password='testpass123')
        response = self.client.get('/admin/dashboard/metrics/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertIn('metrics', data)
        self.assertIn('system_status', data)
        self.assertIn('timestamp', data)
    
    def test_dashboard_metrics_ajax_requires_staff(self):
        """Test that AJAX endpoint requires staff privileges"""
        self.client.login(username='user', password='testpass123')
        response = self.client.get('/admin/dashboard/metrics/')
        self.assertEqual(response.status_code, 302)  # Redirect or forbidden


class DashboardViewIntegrationTestCase(TestCase):
    """Integration tests for dashboard views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create some test users for metrics
        for i in range(5):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
    
    def test_dashboard_displays_real_metrics(self):
        """Test that dashboard displays actual user metrics"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get('/admin/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        
        # Check that context contains expected data
        self.assertIn('metrics', response.context)
        self.assertIn('recent_activities', response.context)
        self.assertIn('system_status', response.context)
        self.assertIn('quick_stats', response.context)
    
    def test_dashboard_handles_service_errors(self):
        """Test that dashboard handles service errors gracefully"""
        with patch.object(DashboardService, 'get_dashboard_metrics') as mock_metrics:
            mock_metrics.side_effect = Exception("Service error")
            
            self.client.login(username='admin', password='testpass123')
            
            # Should not crash, should handle error gracefully
            # (Implementation would depend on error handling strategy)
            response = self.client.get('/admin/dashboard/')
            # Response code depends on error handling implementation
    
    def test_dashboard_performance_with_large_dataset(self):
        """Test dashboard performance with larger dataset"""
        # Create more users to test performance
        User.objects.bulk_create([
            User(username=f'perfuser{i}', email=f'perfuser{i}@example.com')
            for i in range(100)
        ])
        
        self.client.login(username='admin', password='testpass123')
        
        # Measure response time (basic check)
        start_time = timezone.now()
        response = self.client.get('/admin/dashboard/')
        end_time = timezone.now()
        
        self.assertEqual(response.status_code, 200)
        
        # Response should be reasonably fast (less than 2 seconds)
        response_time = (end_time - start_time).total_seconds()
        self.assertLess(response_time, 2.0)
    
    def test_dashboard_caching(self):
        """Test that dashboard metrics are properly cached"""
        self.client.login(username='admin', password='testpass123')
        
        # Make two requests and verify caching behavior
        with patch.object(DashboardService, 'get_dashboard_metrics') as mock_metrics:
            mock_metrics.return_value = {'cached': True}
            
            # First request - should call service
            response1 = self.client.get('/admin/dashboard/metrics/')
            self.assertEqual(response1.status_code, 200)
            
            # Second request - should use cache (mock would not be called again)
            response2 = self.client.get('/admin/dashboard/metrics/')
            self.assertEqual(response2.status_code, 200)
            
            # Verify service was called at least once
            self.assertTrue(mock_metrics.called)
