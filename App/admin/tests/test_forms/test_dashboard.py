"""
Tests for Admin Dashboard Forms
"""
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone

from ...forms.dashboard import DashboardFilterForm


class DashboardFilterFormTestCase(TestCase):
    """Test cases for dashboard filter form"""
    
    def test_form_valid_with_defaults(self):
        """Test form is valid with default values"""
        form = DashboardFilterForm({})
        self.assertTrue(form.is_valid())
        
        # Check default values
        self.assertEqual(form.cleaned_data['period'], 'last_7_days')
        self.assertEqual(form.cleaned_data['metric_type'], 'all')
        self.assertEqual(form.cleaned_data['refresh_interval'], 30)
    
    def test_form_valid_with_all_fields(self):
        """Test form is valid with all fields provided"""
        data = {
            'period': 'last_30_days',
            'metric_type': 'users',
            'refresh_interval': 60
        }
        form = DashboardFilterForm(data)
        self.assertTrue(form.is_valid())
        
        # Check cleaned data
        self.assertEqual(form.cleaned_data['period'], 'last_30_days')
        self.assertEqual(form.cleaned_data['metric_type'], 'users')
        self.assertEqual(form.cleaned_data['refresh_interval'], 60)
    
    def test_custom_period_requires_dates(self):
        """Test custom period validation requires both dates"""
        data = {
            'period': 'custom',
            'metric_type': 'all'
        }
        form = DashboardFilterForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('Custom date range requires both start and end dates', 
                     form.errors['__all__'][0])
    
    def test_custom_period_with_valid_dates(self):
        """Test custom period with valid date range"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        data = {
            'period': 'custom',
            'date_from': yesterday,
            'date_to': today,
            'metric_type': 'all'
        }
        form = DashboardFilterForm(data)
        self.assertTrue(form.is_valid())
    
    def test_custom_period_with_invalid_date_range(self):
        """Test custom period with invalid date range (start > end)"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        data = {
            'period': 'custom',
            'date_from': tomorrow,  # Future date
            'date_to': today,       # Earlier date
            'metric_type': 'all'
        }
        form = DashboardFilterForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('Start date must be before end date', 
                     form.errors['__all__'][0])
    
    def test_period_choices(self):
        """Test all period choices are valid"""
        valid_periods = [
            'today', 'yesterday', 'last_7_days', 
            'last_30_days', 'last_90_days', 'custom'
        ]
        
        for period in valid_periods:
            data = {'period': period}
            if period == 'custom':
                # Custom period needs dates
                data.update({
                    'date_from': date.today() - timedelta(days=1),
                    'date_to': date.today()
                })
            
            form = DashboardFilterForm(data)
            self.assertTrue(form.is_valid(), f"Period '{period}' should be valid")
    
    def test_metric_type_choices(self):
        """Test all metric type choices are valid"""
        valid_metrics = ['all', 'users', 'revenue', 'transactions', 'system']
        
        for metric_type in valid_metrics:
            data = {'metric_type': metric_type}
            form = DashboardFilterForm(data)
            self.assertTrue(form.is_valid(), f"Metric type '{metric_type}' should be valid")
    
    def test_refresh_interval_validation(self):
        """Test refresh interval validation"""
        # Valid intervals
        for interval in [10, 30, 60, 120, 300]:
            data = {'refresh_interval': interval}
            form = DashboardFilterForm(data)
            self.assertTrue(form.is_valid(), f"Interval {interval} should be valid")
        
        # Invalid intervals (too low)
        data = {'refresh_interval': 5}
        form = DashboardFilterForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('refresh_interval', form.errors)
        
        # Invalid intervals (too high)
        data = {'refresh_interval': 400}
        form = DashboardFilterForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('refresh_interval', form.errors)
    
    def test_form_widget_attributes(self):
        """Test form widgets have correct CSS classes and attributes"""
        form = DashboardFilterForm()
        
        # Check period field widget
        period_widget = form.fields['period'].widget
        self.assertIn('form-control', period_widget.attrs.get('class', ''))
        self.assertEqual(period_widget.attrs.get('id'), 'dashboard-period')
        
        # Check metric type field widget
        metric_widget = form.fields['metric_type'].widget
        self.assertIn('form-control', metric_widget.attrs.get('class', ''))
        self.assertEqual(metric_widget.attrs.get('id'), 'dashboard-metric-type')
        
        # Check date fields have date input type
        date_from_widget = form.fields['date_from'].widget
        self.assertEqual(date_from_widget.attrs.get('type'), 'date')
        
        date_to_widget = form.fields['date_to'].widget
        self.assertEqual(date_to_widget.attrs.get('type'), 'date')
    
    def test_form_field_labels(self):
        """Test form field labels are correctly set"""
        form = DashboardFilterForm()
        
        self.assertEqual(str(form.fields['period'].label), 'Time Period')
        self.assertEqual(str(form.fields['metric_type'].label), 'Metric Type')
        self.assertEqual(str(form.fields['date_from'].label), 'From Date')
        self.assertEqual(str(form.fields['date_to'].label), 'To Date')
        self.assertEqual(str(form.fields['refresh_interval'].label), 'Refresh Interval (seconds)')
    
    def test_form_optional_fields(self):
        """Test that date fields are optional for non-custom periods"""
        data = {
            'period': 'last_7_days',
            'metric_type': 'users',
            # No date fields provided
        }
        form = DashboardFilterForm(data)
        self.assertTrue(form.is_valid())
        
        # Date fields should be None in cleaned data
        self.assertIsNone(form.cleaned_data.get('date_from'))
        self.assertIsNone(form.cleaned_data.get('date_to'))
    
    def test_form_rendering(self):
        """Test form can be rendered without errors"""
        form = DashboardFilterForm()
        
        # Should be able to render form fields
        form_html = str(form)
        self.assertIn('dashboard-period', form_html)
        self.assertIn('dashboard-metric-type', form_html)
        self.assertIn('dashboard-date-from', form_html)
        self.assertIn('dashboard-date-to', form_html)
        self.assertIn('dashboard-refresh-interval', form_html)
    
    def test_form_with_initial_data(self):
        """Test form with initial data"""
        initial_data = {
            'period': 'last_30_days',
            'metric_type': 'revenue',
            'refresh_interval': 60
        }
        form = DashboardFilterForm(initial=initial_data)
        
        # Check initial values are set
        self.assertEqual(form.initial['period'], 'last_30_days')
        self.assertEqual(form.initial['metric_type'], 'revenue')
        self.assertEqual(form.initial['refresh_interval'], 60)
