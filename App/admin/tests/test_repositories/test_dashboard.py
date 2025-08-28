"""
Tests for Admin Dashboard Repository
"""
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock

from ...repositories.dashboard_repository import DashboardRepository
from ...models.audit_log import AdminAuditLog

User = get_user_model()


class DashboardRepositoryTestCase(TestCase):
    """Test cases for dashboard repository"""
    
    def setUp(self):
        """Set up test data"""
        self.repository = DashboardRepository()
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create some regular users
        self.users = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
            self.users.append(user)
    
    def test_get_user_metrics_all_users(self):
        """Test getting all user metrics"""
        metrics = self.repository.get_user_metrics()
        
        # Should include admin user + 5 regular users
        self.assertEqual(metrics['total_users'], 6)
        self.assertEqual(metrics['new_users'], 6)  # All users are "new" without date filter
    
    def test_get_user_metrics_with_date_filter(self):
        """Test getting user metrics with date filtering"""
        # Create a user with specific date
        old_date = timezone.now() - timedelta(days=10)
        
        with patch('django.utils.timezone.now', return_value=old_date):
            old_user = User.objects.create_user(
                username='olduser',
                email='olduser@example.com',
                password='testpass123'
            )
        
        # Get metrics for last 5 days (should exclude old user)
        start_date = timezone.now() - timedelta(days=5)
        metrics = self.repository.get_user_metrics(start_date=start_date)
        
        # Should not include the old user
        self.assertLess(metrics['new_users'], metrics['total_users'])
    
    def test_get_user_metrics_active_users(self):
        """Test getting active user count"""
        # Set some users as recently active
        recent_login = timezone.now() - timedelta(days=15)
        
        for user in self.users[:2]:
            user.last_login = recent_login
            user.save()
        
        metrics = self.repository.get_user_metrics()
        
        # Should have 2 active users (logged in within 30 days)
        self.assertEqual(metrics['active_users'], 2)
    
    def test_get_business_metrics_no_business_model(self):
        """Test business metrics when business model is not available"""
        metrics = self.repository.get_business_metrics()
        
        # Should return zero values when business model not available
        self.assertEqual(metrics['total_businesses'], 0)
        self.assertEqual(metrics['new_businesses'], 0)
        self.assertEqual(metrics['active_businesses'], 0)
        self.assertEqual(metrics['verified_businesses'], 0)
    
    @patch('App.admin.repositories.dashboard_repository.Business')
    def test_get_business_metrics_with_business_model(self, mock_business):
        """Test business metrics when business model is available"""
        # Mock business queryset
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 10
        mock_queryset.filter.return_value = mock_queryset
        mock_business.objects.all.return_value = mock_queryset
        mock_business.objects.count.return_value = 15
        
        metrics = self.repository.get_business_metrics()
        
        self.assertEqual(metrics['total_businesses'], 15)
        self.assertEqual(metrics['new_businesses'], 10)
    
    def test_get_financial_metrics_placeholder(self):
        """Test financial metrics returns placeholder data"""
        metrics = self.repository.get_financial_metrics()
        
        # Should return placeholder zero values
        self.assertEqual(metrics['total_revenue'], 0)
        self.assertEqual(metrics['monthly_revenue'], 0)
        self.assertEqual(metrics['pending_payouts'], 0)
        self.assertEqual(metrics['completed_transactions'], 0)
        self.assertEqual(metrics['failed_transactions'], 0)
    
    @patch('django.db.connection')
    def test_get_system_metrics(self, mock_connection):
        """Test system metrics database queries"""
        # Mock database cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [1024000]  # 1MB database size
        mock_cursor.fetchall.return_value = [
            ('public', 'users', 100),
            ('public', 'businesses', 50)
        ]
        mock_cursor.rowcount = 1
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.queries.__len__.return_value = 5
        
        metrics = self.repository.get_system_metrics()
        
        self.assertEqual(metrics['database_size'], 1024000)
        self.assertEqual(metrics['active_connections'], 5)
        self.assertEqual(len(metrics['table_operations']), 2)
    
    def test_get_recent_activities(self):
        """Test getting recent admin activities"""
        # Create some audit log entries
        for i in range(3):
            AdminAuditLog.objects.create(
                admin_user=self.admin_user,
                action='CREATE',
                target_model='User',
                target_id=str(self.users[i].id),
                description=f'Created user {i}'
            )
        
        activities = self.repository.get_recent_activities(limit=5)
        
        self.assertEqual(len(activities), 3)
        self.assertEqual(activities[0].admin_user, self.admin_user)
    
    def test_get_recent_activities_ordering(self):
        """Test that recent activities are ordered by created_at desc"""
        # Create activities with different timestamps
        old_activity = AdminAuditLog.objects.create(
            admin_user=self.admin_user,
            action='CREATE',
            target_model='User',
            description='Old activity'
        )
        
        # Make the activity older
        old_time = timezone.now() - timedelta(hours=1)
        AdminAuditLog.objects.filter(id=old_activity.id).update(created_at=old_time)
        
        new_activity = AdminAuditLog.objects.create(
            admin_user=self.admin_user,
            action='UPDATE',
            target_model='User',
            description='New activity'
        )
        
        activities = self.repository.get_recent_activities(limit=5)
        
        # Newest should be first
        self.assertEqual(activities[0].id, new_activity.id)
        self.assertEqual(activities[1].id, old_activity.id)
    
    def test_get_top_performing_items_users(self):
        """Test getting top performing users"""
        items = self.repository.get_top_performing_items('users', limit=3)
        
        self.assertEqual(len(items), 3)  # Should return 3 most recent users
        # All returned items should be User objects
        for item in items:
            self.assertIsInstance(item, User)
    
    def test_get_top_performing_items_businesses(self):
        """Test getting top performing businesses (when no business model)"""
        items = self.repository.get_top_performing_items('businesses', limit=3)
        
        self.assertEqual(len(items), 0)  # Should return empty list
    
    def test_get_growth_trends(self):
        """Test getting growth trends data"""
        trends = self.repository.get_growth_trends(days=7)
        
        self.assertIn('user_growth', trends)
        self.assertIn('business_growth', trends)
        self.assertIn('revenue_growth', trends)
        
        # Should have 8 data points (7 days + today)
        self.assertEqual(len(trends['user_growth']), 8)
        
        # Each data point should have date and count
        for point in trends['user_growth']:
            self.assertIn('date', point)
            self.assertIn('count', point)
    
    def test_get_growth_trends_user_counts(self):
        """Test that growth trends show correct user counts"""
        # Create users on specific dates
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Create user yesterday
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = timezone.make_aware(
                datetime.combine(yesterday, datetime.min.time())
            )
            yesterday_user = User.objects.create_user(
                username='yesterdayuser',
                email='yesterday@example.com',
                password='testpass123'
            )
        
        trends = self.repository.get_growth_trends(days=2)
        
        # Find yesterday's data point
        yesterday_data = None
        for point in trends['user_growth']:
            if point['date'] == yesterday:
                yesterday_data = point
                break
        
        self.assertIsNotNone(yesterday_data)
        self.assertGreater(yesterday_data['count'], 0)
    
    @patch('django.db.connection')
    def test_get_system_status_healthy(self, mock_connection):
        """Test system status when database is healthy"""
        # Mock successful database query
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        status = self.repository.get_system_status()
        
        self.assertEqual(status['database'], 'healthy')
        self.assertEqual(status['cache'], 'healthy')
        self.assertEqual(status['storage'], 'healthy')
        self.assertEqual(status['external_apis'], 'healthy')
    
    @patch('django.db.connection')
    def test_get_system_status_database_error(self, mock_connection):
        """Test system status when database has error"""
        # Mock database exception
        mock_connection.cursor.side_effect = Exception("Database error")
        
        status = self.repository.get_system_status()
        
        self.assertEqual(status['database'], 'error')
    
    def test_repository_methods_exist(self):
        """Test that all required repository methods exist"""
        required_methods = [
            'get_user_metrics',
            'get_business_metrics',
            'get_financial_metrics',
            'get_system_metrics',
            'get_recent_activities',
            'get_top_performing_items',
            'get_growth_trends',
            'get_system_status'
        ]
        
        for method_name in required_methods:
            self.assertTrue(
                hasattr(self.repository, method_name),
                f"Repository should have {method_name} method"
            )
            self.assertTrue(
                callable(getattr(self.repository, method_name)),
                f"{method_name} should be callable"
            )
