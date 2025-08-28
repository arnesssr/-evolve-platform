"""
Admin Admins Repository
Data access layer for admin user management
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q, Count
from django.utils import timezone

User = get_user_model()


class AdminsRepository:
    """
    Repository for admin user data access
    """
    
    def get_admin_users(self, filters=None):
        """
        Get filtered list of admin users
        """
        queryset = User.objects.filter(is_staff=True).select_related().prefetch_related('groups')
        
        if not filters:
            return queryset.order_by('-date_joined')
        
        # Apply search filter
        if 'search' in filters:
            search_term = filters['search']
            queryset = queryset.filter(
                Q(username__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term)
            )
        
        # Apply status filter
        if 'is_active' in filters:
            queryset = queryset.filter(is_active=filters['is_active'])
        
        # Apply superuser filter
        if 'is_superuser' in filters:
            queryset = queryset.filter(is_superuser=filters['is_superuser'])
        
        # Apply group filter
        if 'groups' in filters:
            queryset = queryset.filter(groups=filters['groups'])
        
        return queryset.order_by('-date_joined')
    
    def get_admin_user_by_id(self, user_id):
        """
        Get admin user by ID
        """
        try:
            return User.objects.get(id=user_id, is_staff=True)
        except User.DoesNotExist:
            return None
    
    def create_admin_user(self, user_data):
        """
        Create new admin user
        """
        # Extract groups data if present
        groups_data = user_data.pop('groups', [])
        
        # Create user
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            password=user_data['password1'],  # From UserCreationForm
            is_staff=True,
            is_active=True,
            is_superuser=user_data.get('is_superuser', False)
        )
        
        # Set groups if provided
        if groups_data:
            user.groups.set(groups_data)
        
        return user
    
    def update_admin_user(self, user_id, user_data):
        """
        Update existing admin user
        """
        user = self.get_admin_user_by_id(user_id)
        if not user:
            return None
        
        # Extract groups data if present
        groups_data = user_data.pop('groups', None)
        
        # Update user fields
        for field, value in user_data.items():
            if hasattr(user, field) and field not in ['password1', 'password2']:
                setattr(user, field, value)
        
        user.save()
        
        # Update groups if provided
        if groups_data is not None:
            user.groups.set(groups_data)
        
        return user
    
    def get_admin_stats(self):
        """
        Get admin user statistics
        """
        total_admins = User.objects.filter(is_staff=True).count()
        active_admins = User.objects.filter(is_staff=True, is_active=True).count()
        inactive_admins = total_admins - active_admins
        superusers = User.objects.filter(is_staff=True, is_superuser=True).count()
        
        # Get recent registrations (last 30 days)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_admins = User.objects.filter(
            is_staff=True,
            date_joined__gte=thirty_days_ago
        ).count()
        
        # Get group distribution
        groups_stats = Group.objects.annotate(
            admin_count=Count('user', filter=Q(user__is_staff=True))
        ).filter(admin_count__gt=0).order_by('-admin_count')[:5]
        
        return {
            'total_admins': total_admins,
            'active_admins': active_admins,
            'inactive_admins': inactive_admins,
            'superusers': superusers,
            'recent_admins': recent_admins,
            'top_groups': [
                {'name': group.name, 'count': group.admin_count}
                for group in groups_stats
            ]
        }
