"""
Admin Admins Service
Business logic for admin user management
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.utils.crypto import get_random_string
from django.db import transaction

from ..repositories.admins_repository import AdminsRepository
from ..exceptions.admin_exceptions import AdminOperationError
from .audit_service import AuditService

User = get_user_model()


class AdminsService:
    """
    Service for admin user management business logic
    """
    
    def __init__(self):
        self.repository = AdminsRepository()
        self.audit_service = AuditService()
    
    def get_admin_users(self, filters=None):
        """
        Get filtered list of admin users
        """
        try:
            return self.repository.get_admin_users(filters or {})
        except Exception as e:
            raise AdminOperationError(f"Failed to retrieve admin users: {str(e)}")
    
    def get_admin_stats(self):
        """
        Get admin user statistics
        """
        try:
            return self.repository.get_admin_stats()
        except Exception as e:
            raise AdminOperationError(f"Failed to retrieve admin statistics: {str(e)}")
    
    @transaction.atomic
    def create_admin_user(self, user_data, created_by):
        """
        Create new admin user
        """
        try:
            # Check if username already exists
            if User.objects.filter(username=user_data['username']).exists():
                raise AdminOperationError(f"Username '{user_data['username']}' already exists")
            
            # Check if email already exists
            if User.objects.filter(email=user_data['email']).exists():
                raise AdminOperationError(f"Email '{user_data['email']}' already exists")
            
            # Create user
            admin_user = self.repository.create_admin_user(user_data)
            
            # Log the action
            self.audit_service.log_action(
                admin_user=created_by,
                action='CREATE',
                target_model='User',
                target_id=str(admin_user.id),
                description=f'Created admin user: {admin_user.username}'
            )
            
            return admin_user
            
        except AdminOperationError:
            raise
        except Exception as e:
            raise AdminOperationError(f"Failed to create admin user: {str(e)}")
    
    @transaction.atomic
    def update_admin_user(self, user_id, user_data, updated_by):
        """
        Update existing admin user
        """
        try:
            admin_user = self.repository.get_admin_user_by_id(user_id)
            if not admin_user:
                raise AdminOperationError("Admin user not found")
            
            # Check for duplicate username/email (excluding current user)
            if User.objects.filter(username=user_data['username']).exclude(id=user_id).exists():
                raise AdminOperationError(f"Username '{user_data['username']}' already exists")
            
            if User.objects.filter(email=user_data['email']).exclude(id=user_id).exists():
                raise AdminOperationError(f"Email '{user_data['email']}' already exists")
            
            # Update user
            updated_user = self.repository.update_admin_user(user_id, user_data)
            
            # Log the action
            self.audit_service.log_action(
                admin_user=updated_by,
                action='UPDATE',
                target_model='User',
                target_id=str(user_id),
                description=f'Updated admin user: {updated_user.username}'
            )
            
            return updated_user
            
        except AdminOperationError:
            raise
        except Exception as e:
            raise AdminOperationError(f"Failed to update admin user: {str(e)}")
    
    def get_admin_details(self, user_id):
        """
        Get detailed information about admin user
        """
        try:
            admin_user = self.repository.get_admin_user_by_id(user_id)
            if not admin_user:
                raise AdminOperationError("Admin user not found")
            
            return {
                'id': admin_user.id,
                'username': admin_user.username,
                'first_name': admin_user.first_name,
                'last_name': admin_user.last_name,
                'email': admin_user.email,
                'is_active': admin_user.is_active,
                'is_superuser': admin_user.is_superuser,
                'date_joined': admin_user.date_joined,
                'last_login': admin_user.last_login,
                'groups': [group.name for group in admin_user.groups.all()],
                'permissions': list(admin_user.get_all_permissions()),
            }
            
        except AdminOperationError:
            raise
        except Exception as e:
            raise AdminOperationError(f"Failed to get admin details: {str(e)}")
    
    @transaction.atomic
    def toggle_admin_status(self, user_id, updated_by):
        """
        Toggle admin user active status
        """
        try:
            admin_user = self.repository.get_admin_user_by_id(user_id)
            if not admin_user:
                raise AdminOperationError("Admin user not found")
            
            # Prevent self-deactivation
            if str(updated_by.id) == str(user_id) and admin_user.is_active:
                raise AdminOperationError("You cannot deactivate your own account")
            
            admin_user.is_active = not admin_user.is_active
            admin_user.save()
            
            # Log the action
            status = 'activated' if admin_user.is_active else 'deactivated'
            self.audit_service.log_action(
                admin_user=updated_by,
                action='UPDATE',
                target_model='User',
                target_id=str(user_id),
                description=f'{status.title()} admin user: {admin_user.username}'
            )
            
            return admin_user
            
        except AdminOperationError:
            raise
        except Exception as e:
            raise AdminOperationError(f"Failed to toggle admin status: {str(e)}")
    
    @transaction.atomic
    def reset_admin_password(self, user_id, reset_by):
        """
        Reset admin user password
        """
        try:
            admin_user = self.repository.get_admin_user_by_id(user_id)
            if not admin_user:
                raise AdminOperationError("Admin user not found")
            
            # Generate temporary password
            temp_password = get_random_string(12)
            admin_user.set_password(temp_password)
            admin_user.save()
            
            # Log the action
            self.audit_service.log_action(
                admin_user=reset_by,
                action='UPDATE',
                target_model='User',
                target_id=str(user_id),
                description=f'Reset password for admin user: {admin_user.username}'
            )
            
            return temp_password
            
        except AdminOperationError:
            raise
        except Exception as e:
            raise AdminOperationError(f"Failed to reset password: {str(e)}")
    
    @transaction.atomic
    def delete_admin_user(self, user_id, deleted_by):
        """
        Soft delete admin user (deactivate)
        """
        try:
            admin_user = self.repository.get_admin_user_by_id(user_id)
            if not admin_user:
                raise AdminOperationError("Admin user not found")
            
            # Prevent self-deletion
            if str(deleted_by.id) == str(user_id):
                raise AdminOperationError("You cannot delete your own account")
            
            admin_user.is_active = False
            admin_user.save()
            
            # Log the action
            self.audit_service.log_action(
                admin_user=deleted_by,
                action='DELETE',
                target_model='User',
                target_id=str(user_id),
                description=f'Deleted admin user: {admin_user.username}'
            )
            
        except AdminOperationError:
            raise
        except Exception as e:
            raise AdminOperationError(f"Failed to delete admin user: {str(e)}")
    
    @transaction.atomic
    def update_admin_permissions(self, user_id, permission_ids, updated_by):
        """
        Update admin user permissions
        """
        try:
            admin_user = self.repository.get_admin_user_by_id(user_id)
            if not admin_user:
                raise AdminOperationError("Admin user not found")
            
            permissions = Permission.objects.filter(id__in=permission_ids)
            admin_user.user_permissions.set(permissions)
            
            # Log the action
            self.audit_service.log_action(
                admin_user=updated_by,
                action='UPDATE',
                target_model='User',
                target_id=str(user_id),
                description=f'Updated permissions for admin user: {admin_user.username}'
            )
            
        except AdminOperationError:
            raise
        except Exception as e:
            raise AdminOperationError(f"Failed to update permissions: {str(e)}")
    
    def get_admin_permissions(self, user_id):
        """
        Get admin user permissions
        """
        try:
            admin_user = self.repository.get_admin_user_by_id(user_id)
            if not admin_user:
                raise AdminOperationError("Admin user not found")
            
            all_permissions = Permission.objects.all().select_related('content_type')
            user_permissions = admin_user.user_permissions.all()
            
            permissions_data = []
            for perm in all_permissions:
                permissions_data.append({
                    'id': perm.id,
                    'name': perm.name,
                    'codename': perm.codename,
                    'content_type': perm.content_type.name,
                    'assigned': perm in user_permissions
                })
            
            return {
                'user': {
                    'id': admin_user.id,
                    'username': admin_user.username,
                    'is_superuser': admin_user.is_superuser
                },
                'permissions': permissions_data
            }
            
        except AdminOperationError:
            raise
        except Exception as e:
            raise AdminOperationError(f"Failed to get permissions: {str(e)}")
    
    def get_admin_activity_log(self, user_id, limit=50):
        """
        Get admin user activity log
        """
        try:
            admin_user = self.repository.get_admin_user_by_id(user_id)
            if not admin_user:
                raise AdminOperationError("Admin user not found")
            
            activities = self.audit_service.get_user_activities(admin_user.id, limit=limit)
            
            return [{
                'id': activity.id,
                'action': activity.action,
                'target_model': activity.target_model,
                'target_id': activity.target_id,
                'description': activity.description,
                'created_at': activity.created_at,
                'ip_address': activity.ip_address,
            } for activity in activities]
            
        except AdminOperationError:
            raise
        except Exception as e:
            raise AdminOperationError(f"Failed to get activity log: {str(e)}")
