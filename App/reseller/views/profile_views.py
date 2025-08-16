"""Views for reseller profile management."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction

from ..earnings.models.reseller import Reseller
from ..earnings.services.reseller_service import ResellerService
from ..earnings.forms.profile_forms import (
    ResellerProfileForm, PaymentMethodForm,
    ProfileSetupWizardForm, ProfileVerificationForm
)


@login_required
def profile_view(request):
    """Display reseller profile."""
    try:
        reseller = request.user.reseller_profile
    except Reseller.DoesNotExist:
        return redirect('reseller:profile_setup')
    
    service = ResellerService()
    
    # Get profile statistics
    stats = service.get_reseller_stats(reseller.id)
    
    # Get profile completion status
    completion_status = service.get_profile_completion_status(reseller.id)
    
    context = {
        'reseller': reseller,
        'stats': stats,
        'completion_status': completion_status,
        'page_title': 'My Profile'
    }
    
    return render(request, 'dashboards/reseller/pages/profile/view_profile.html', context)


@login_required
def profile_edit(request):
    """Edit reseller profile information."""
    try:
        reseller = request.user.reseller_profile
    except Reseller.DoesNotExist:
        return redirect('reseller:profile_setup')
    
    if request.method == 'POST':
        form = ResellerProfileForm(request.POST, instance=reseller)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('reseller:profile_view')
    else:
        form = ResellerProfileForm(instance=reseller)
    
    context = {
        'form': form,
        'reseller': reseller,
        'page_title': 'Edit Profile'
    }
    
    return render(request, 'dashboards/reseller/pages/profile/edit_profile.html', context)


@login_required
def payment_method_update(request):
    """Update payment method information."""
    try:
        reseller = request.user.reseller_profile
    except Reseller.DoesNotExist:
        return redirect('reseller:profile_setup')
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=reseller)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment method updated successfully!')
            return redirect('reseller:profile_view')
    else:
        form = PaymentMethodForm(instance=reseller)
    
    context = {
        'form': form,
        'reseller': reseller,
        'page_title': 'Update Payment Method'
    }
    
    return render(request, 'dashboards/reseller/pages/profile/payment_method.html', context)


@login_required
def profile_setup(request):
    """Initial profile setup wizard for new resellers."""
    # Check if user already has a profile
    if hasattr(request.user, 'reseller_profile'):
        return redirect('reseller:profile_view')
    
    if request.method == 'POST':
        form = ProfileSetupWizardForm(request.POST)
        if form.is_valid():
            service = ResellerService()
            try:
                # Create reseller profile
                profile_data = form.cleaned_data
                reseller = service.create_reseller_profile(
                    user=request.user,
                    profile_data=profile_data
                )
                
                messages.success(request, 'Profile created successfully! Welcome to our reseller program.')
                return redirect('reseller:dashboard')
                
            except Exception as e:
                messages.error(request, f'Error creating profile: {str(e)}')
    else:
        form = ProfileSetupWizardForm()
    
    context = {
        'form': form,
        'page_title': 'Setup Your Profile'
    }
    
    return render(request, 'dashboards/reseller/pages/profile/profile_wizard.html', context)


@login_required
def profile_verification(request):
    """Request profile verification."""
    try:
        reseller = request.user.reseller_profile
    except Reseller.DoesNotExist:
        return redirect('reseller:profile_setup')
    
    # Check if already verified
    if reseller.is_verified:
        messages.info(request, 'Your profile is already verified.')
        return redirect('reseller:profile_view')
    
    if request.method == 'POST':
        form = ProfileVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            # TODO: Handle verification document upload and processing
            # For now, just mark as pending verification
            messages.success(
                request, 
                'Verification request submitted! We will review your documents and notify you within 2-3 business days.'
            )
            return redirect('reseller:profile_view')
    else:
        form = ProfileVerificationForm()
    
    context = {
        'form': form,
        'reseller': reseller,
        'page_title': 'Verify Your Profile'
    }
    
    return render(request, 'dashboards/reseller/pages/profile/profile_verification.html', context)


@login_required
@require_http_methods(["GET"])
def profile_completion_status(request):
    """Get profile completion status via AJAX."""
    try:
        reseller = request.user.reseller_profile
        service = ResellerService()
        
        completion_status = service.get_profile_completion_status(reseller.id)
        
        return JsonResponse({
            'success': True,
            'data': completion_status
        })
        
    except Reseller.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Profile not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def profile_stats(request):
    """Display detailed profile statistics."""
    try:
        reseller = request.user.reseller_profile
    except Reseller.DoesNotExist:
        return redirect('reseller:profile_setup')
    
    service = ResellerService()
    
    # Get comprehensive statistics
    stats = service.get_reseller_stats(reseller.id)
    
    # Get recent commission history
    from ..earnings.services.commission_service import CommissionService
    commission_service = CommissionService()
    recent_commissions = commission_service.get_reseller_commissions(
        reseller.id, 
        limit=10
    )
    
    context = {
        'reseller': reseller,
        'stats': stats,
        'recent_commissions': recent_commissions,
        'page_title': 'Profile Statistics'
    }
    
    return render(request, 'dashboards/reseller/pages/profile/profile_stats.html', context)


@login_required
def deactivate_profile(request):
    """Deactivate reseller profile."""
    if request.method == 'POST':
        try:
            reseller = request.user.reseller_profile
            service = ResellerService()
            
            # Deactivate the profile
            service.deactivate_reseller(reseller.id)
            
            messages.warning(request, 'Your reseller profile has been deactivated.')
            return redirect('home')  # Redirect to main home page
            
        except Exception as e:
            messages.error(request, f'Error deactivating profile: {str(e)}')
            return redirect('reseller:profile_view')
    
    return render(request, 'dashboards/reseller/pages/profile/deactivate_confirm.html')
