"""
Admin Admins Views
Handles admin user management - list and form pages
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from App.admin.permissions import admin_required

from ..services.admins_service import AdminsService
from ..forms.admins import AdminCreateForm, AdminUpdateForm, AdminFilterForm
from ..exceptions.admin_exceptions import AdminOperationError

User = get_user_model()


@login_required
@admin_required
def admins_list_view(request):
    """
    List view for admin users
    Shows paginated list with search and filtering
    """
    service = AdminsService()
    filter_form = AdminFilterForm(request.GET or None)
    
    # Get filtered admin users
    filters = {}
    if filter_form.is_valid():
        filters = filter_form.get_filter_params()
    
    admins = service.get_admin_users(filters=filters)
    
    # Pagination
    paginator = Paginator(admins, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'total_admins': paginator.count,
        'stats': service.get_admin_stats(),
    }
    
    return render(request, 'dashboards/admin/pages/admins/list.html', context)


@login_required
@admin_required
def admin_create_view(request):
    """
    Create new admin user
    """
    service = AdminsService()
    
    if request.method == 'POST':
        form = AdminCreateForm(request.POST)
        if form.is_valid():
            try:
                admin_user = service.create_admin_user(
                    user_data=form.cleaned_data,
                    created_by=request.user
                )
                
                messages.success(
                    request, 
                    f'Admin user "{admin_user.username}" created successfully.'
                )
                return redirect('platform_admin:admin_admins:list')
                
            except AdminOperationError as e:
                messages.error(request, str(e))
    else:
        form = AdminCreateForm()
    
    context = {
        'form': form,
        'title': 'Create Admin User',
        'action': 'Create',
    }
    
    return render(request, 'dashboards/admin/pages/admins/form.html', context)


@login_required
@admin_required
def admin_update_view(request, user_id):
    """
    Update existing admin user
    """
    service = AdminsService()
    admin_user = get_object_or_404(User, id=user_id, is_staff=True)
    
    if request.method == 'POST':
        form = AdminUpdateForm(request.POST, instance=admin_user)
        if form.is_valid():
            try:
                updated_user = service.update_admin_user(
                    user_id=user_id,
                    user_data=form.cleaned_data,
                    updated_by=request.user
                )
                
                messages.success(
                    request,
                    f'Admin user "{updated_user.username}" updated successfully.'
                )
                return redirect('platform_admin:admin_admins:list')
                
            except AdminOperationError as e:
                messages.error(request, str(e))
    else:
        form = AdminUpdateForm(instance=admin_user)
    
    context = {
        'form': form,
        'admin_user': admin_user,
        'title': f'Update Admin User: {admin_user.username}',
        'action': 'Update',
    }
    
    return render(request, 'dashboards/admin/pages/admins/form.html', context)


@login_required
@admin_required
def admin_detail_view(request, user_id):
    """
    Detail view for admin user (AJAX)
    """
    service = AdminsService()
    
    try:
        admin_details = service.get_admin_details(user_id)
        return JsonResponse({
            'success': True,
            'data': admin_details
        })
    except AdminOperationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@admin_required
@require_POST
def admin_toggle_status_view(request, user_id):
    """
    Toggle admin user active status (AJAX)
    """
    service = AdminsService()
    
    try:
        admin_user = service.toggle_admin_status(
            user_id=user_id,
            updated_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'is_active': admin_user.is_active,
            'message': f'Admin status updated successfully.'
        })
        
    except AdminOperationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@admin_required
@require_POST
def admin_reset_password_view(request, user_id):
    """
    Reset admin user password (AJAX)
    """
    service = AdminsService()
    
    try:
        temp_password = service.reset_admin_password(
            user_id=user_id,
            reset_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'temp_password': temp_password,
            'message': 'Password reset successfully. Please share the temporary password securely.'
        })
        
    except AdminOperationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@admin_required
@require_POST
def admin_delete_view(request, user_id):
    """
    Soft delete admin user (AJAX)
    """
    service = AdminsService()
    
    # Prevent self-deletion
    if str(request.user.id) == str(user_id):
        return JsonResponse({
            'success': False,
            'error': 'You cannot delete your own admin account.'
        }, status=400)
    
    try:
        service.delete_admin_user(
            user_id=user_id,
            deleted_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Admin user deactivated successfully.'
        })
        
    except AdminOperationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@admin_required
def admin_permissions_view(request, user_id):
    """
    Manage admin user permissions (AJAX)
    """
    service = AdminsService()
    admin_user = get_object_or_404(User, id=user_id, is_staff=True)
    
    if request.method == 'POST':
        permission_ids = request.POST.getlist('permissions')
        
        try:
            service.update_admin_permissions(
                user_id=user_id,
                permission_ids=permission_ids,
                updated_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Permissions updated successfully.'
            })
            
        except AdminOperationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # GET request - return current permissions
    permissions_data = service.get_admin_permissions(user_id)
    return JsonResponse({
        'success': True,
        'data': permissions_data
    })


@login_required
@admin_required
def admin_activity_log_view(request, user_id):
    """
    Get admin user activity log (AJAX)
    """
    service = AdminsService()
    limit = int(request.GET.get('limit', 50))
    
    try:
        activities = service.get_admin_activity_log(user_id, limit=limit)
        
        return JsonResponse({
            'success': True,
            'data': activities
        })
        
    except AdminOperationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
