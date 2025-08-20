from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.utils.crypto import get_random_string

from App.business.models import BusinessUser, Department, Software

@login_required
def user_management(request):
    # Assume business is linked to logged-in user (BusinessUser)
    business_user = get_object_or_404(BusinessUser, user=request.user)
    business = business_user.business

    users = BusinessUser.objects.filter(business=business).select_related("user", "department").prefetch_related("software_access")

    context = {
        "users": users,
        "total_users": users.count(),
        "active_users": users.filter(status="active").count(),
        "pending_users": users.filter(status="pending").count(),
        "admins": users.filter(role="admin").count(),
        "departments": Department.objects.filter(business=business),
        "software_list": Software.objects.all(),
    }
    
    return render(request, "dashboards/business/pages/user-management.html", context)


@login_required
@transaction.atomic
def add_user(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        role = request.POST.get("role")
        department_id = request.POST.get("department")
        software_ids = request.POST.getlist("software")

        # Create base Django User
        temp_password=get_random_string(12)
        new_user = User.objects.create_user(
            username=email,  # email as username
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=temp_password  # Generates a random 12-character password
        )

        # Link to business
        business_user = BusinessUser.objects.create(
            user=new_user,
            business=get_object_or_404(BusinessUser, user=request.user).business,
            role=role,
            status="pending",
            department_id=department_id if department_id else None,
        )

        if software_ids:
            business_user.software_access.set(software_ids)

        messages.success(request, f"User {first_name} {last_name} added successfully!")
        return redirect("business:user_management")

    return redirect("business:user_management")


@login_required
def toggle_user_status(request, user_id):
    business = get_object_or_404(BusinessUser, user=request.user).business
    business_user = get_object_or_404(BusinessUser, id=user_id, business=business)

    if business_user.status == "active":
        business_user.status = "suspended"
    else:
        business_user.status = "active"
    business_user.save()

    messages.info(request, f"User {business_user.user.get_full_name()} status updated to {business_user.status}.")
    return redirect("business:user_management")