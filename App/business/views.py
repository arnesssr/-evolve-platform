from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Create your business views here.

@login_required
def dashboard(request):
    """Main business dashboard view"""
    return HttpResponse("Business Dashboard - Coming Soon")
    # TODO: Implement business dashboard template
