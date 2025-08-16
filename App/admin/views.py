from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Create your admin views here.

@login_required
def dashboard(request):
    """Main admin dashboard view"""
    return HttpResponse("Admin Dashboard - Coming Soon")
    # TODO: Implement admin dashboard template
