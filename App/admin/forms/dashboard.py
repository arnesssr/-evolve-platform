"""
Admin Dashboard Forms
Form classes for dashboard filtering and interactions
"""
from django import forms
from django.utils.translation import gettext_lazy as _


class DashboardFilterForm(forms.Form):
    """
    Form for filtering dashboard data by date range and metrics
    """
    PERIOD_CHOICES = [
        ('today', _('Today')),
        ('yesterday', _('Yesterday')),
        ('last_7_days', _('Last 7 Days')),
        ('last_30_days', _('Last 30 Days')),
        ('last_90_days', _('Last 90 Days')),
        ('custom', _('Custom Range')),
    ]
    
    METRIC_CHOICES = [
        ('all', _('All Metrics')),
        ('users', _('Users')),
        ('revenue', _('Revenue')),
        ('transactions', _('Transactions')),
        ('system', _('System')),
    ]
    
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        initial='last_7_days',
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'id': 'dashboard-period'
        }),
        label=_('Time Period')
    )
    
    metric_type = forms.ChoiceField(
        choices=METRIC_CHOICES,
        initial='all',
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'id': 'dashboard-metric-type'
        }),
        label=_('Metric Type')
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'dashboard-date-from'
        }),
        label=_('From Date')
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'dashboard-date-to'
        }),
        label=_('To Date')
    )
    
    refresh_interval = forms.IntegerField(
        initial=30,
        min_value=10,
        max_value=300,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'dashboard-refresh-interval'
        }),
        label=_('Refresh Interval (seconds)')
    )
    
    def clean(self):
        cleaned_data = super().clean()
        period = cleaned_data.get('period')
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if period == 'custom':
            if not date_from or not date_to:
                raise forms.ValidationError(_('Custom date range requires both start and end dates.'))
            
            if date_from > date_to:
                raise forms.ValidationError(_('Start date must be before end date.'))
        
        return cleaned_data
