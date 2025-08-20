from django.urls import path
from . import views

app_name = "business"

urlpatterns = [
    path("users/", views.user_management, name="user_management"),
    path("users/add/", views.add_user, name="add_user"),
    path("users/<int:user_id>/toggle-status/", views.toggle_user_status, name="toggle_user_status"),
]