"""
Admin Admins URL Configuration
"""
from django.urls import path
from ..views.admins import (
    admins_list_view,
    admin_create_view,
    admin_update_view,
    admin_detail_view,
    admin_toggle_status_view,
    admin_reset_password_view,
    admin_delete_view,
    admin_permissions_view,
    admin_activity_log_view
)

app_name = 'admin_admins'

urlpatterns = [
    path('', admins_list_view, name='list'),
    path('create/', admin_create_view, name='create'),
    path('<int:user_id>/update/', admin_update_view, name='update'),
    path('<int:user_id>/detail/', admin_detail_view, name='detail'),
    path('<int:user_id>/toggle-status/', admin_toggle_status_view, name='toggle_status'),
    path('<int:user_id>/reset-password/', admin_reset_password_view, name='reset_password'),
    path('<int:user_id>/delete/', admin_delete_view, name='delete'),
    path('<int:user_id>/permissions/', admin_permissions_view, name='permissions'),
    path('<int:user_id>/activity-log/', admin_activity_log_view, name='activity_log'),
]
