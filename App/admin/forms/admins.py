"""
Admin Users Forms
Form classes for admin user management
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Permission, Group
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AdminCreateForm(UserCreationForm):
    """Form for creating new admin users"""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        }),
        label=_('First Name')
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        }),
        label=_('Last Name')
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        }),
        label=_('Email Address')
    )
    
    is_superuser = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Is Superuser'),
        help_text=_('Designates that this user has all permissions without explicitly assigning them.')
    )
    
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label=_('Groups')
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_superuser', 'groups')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            })
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True  # All admin users are staff
        user.is_active = True
        if commit:
            user.save()
            self.save_m2m()
        return user


class AdminUpdateForm(UserChangeForm):
    """Form for updating existing admin users"""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        label=_('First Name')
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        label=_('Last Name')
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        }),
        label=_('Email Address')
    )
    
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Is Active')
    )
    
    is_superuser = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Is Superuser')
    )
    
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label=_('Groups')
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser', 'groups')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password field from update form
        if 'password' in self.fields:
            del self.fields['password']


class AdminFilterForm(forms.Form):
    """Form for filtering admin users list"""
    
    STATUS_CHOICES = [
        ('', _('All')),
        ('active', _('Active')),
        ('inactive', _('Inactive')),
    ]
    
    ROLE_CHOICES = [
        ('', _('All')),
        ('superuser', _('Superuser')),
        ('staff', _('Staff')),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, username or email...',
            'id': 'admin-search'
        }),
        label=_('Search')
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'id': 'admin-status-filter'
        }),
        label=_('Status')
    )
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'id': 'admin-role-filter'
        }),
        label=_('Role')
    )
    
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        empty_label=_('All Groups'),
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'id': 'admin-group-filter'
        }),
        label=_('Group')
    )
    
    def get_filter_params(self):
        """Get cleaned filter parameters for the service layer"""
        if not self.is_valid():
            return {}
        
        filters = {}
        
        if self.cleaned_data.get('search'):
            filters['search'] = self.cleaned_data['search']
        
        if self.cleaned_data.get('status'):
            filters['is_active'] = self.cleaned_data['status'] == 'active'
        
        if self.cleaned_data.get('role'):
            if self.cleaned_data['role'] == 'superuser':
                filters['is_superuser'] = True
            elif self.cleaned_data['role'] == 'staff':
                filters['is_superuser'] = False
        
        if self.cleaned_data.get('group'):
            filters['groups'] = self.cleaned_data['group']
        
        return filters
