"""
Management command to ensure all users with reseller role have Reseller profiles.
Fixes "Profile not found" error when resellers try to create marketing links.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from App.models import UserProfile
from App.reseller.earnings.models import Reseller

User = get_user_model()


class Command(BaseCommand):
    help = 'Create Reseller profiles for users with reseller role'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Fixing Reseller Profiles...')
        self.stdout.write('=' * 50)
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        # Find all users with reseller role in UserProfile
        reseller_users = User.objects.filter(
            userprofile__role='reseller'
        ).select_related('userprofile')
        
        self.stdout.write(f'Found {reseller_users.count()} users with reseller role')
        
        for user in reseller_users:
            try:
                # Check if user already has a Reseller profile
                if hasattr(user, 'reseller_profile'):
                    self.stdout.write(f'✅ {user.email} - Reseller profile exists')
                    skipped_count += 1
                    continue
                
                # Create Reseller profile
                with transaction.atomic():
                    # Generate unique referral code
                    referral_code = Reseller.generate_unique_referral_code(user.id)
                    
                    # Create the reseller profile
                    reseller = Reseller.objects.create(
                        user=user,
                        referral_code=referral_code,
                        phone_number=user.userprofile.phone if hasattr(user, 'userprofile') else '',
                        # Set type based on email or other criteria
                        reseller_type='business' if 'business' in user.email.lower() or 'company' in user.email.lower() else 'individual',
                    )
                    
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✨ Created Reseller profile for {user.email} - Code: {referral_code}'
                        )
                    )
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Failed to create profile for {user.email}: {str(e)}'
                    )
                )
        
        # Also check for any users who might be trying to access reseller features
        # without proper role setup
        users_with_reseller_profile_but_wrong_role = User.objects.filter(
            reseller_profile__isnull=False
        ).exclude(
            userprofile__role='reseller'
        ).select_related('userprofile')
        
        if users_with_reseller_profile_but_wrong_role.exists():
            self.stdout.write('\n⚠️  Found users with Reseller profile but incorrect role:')
            for user in users_with_reseller_profile_but_wrong_role:
                if hasattr(user, 'userprofile'):
                    user.userprofile.role = 'reseller'
                    user.userprofile.save()
                    self.stdout.write(
                        self.style.WARNING(
                            f'🔄 Updated role to reseller for {user.email}'
                        )
                    )
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('📊 Summary:')
        self.stdout.write(f'  - Reseller profiles created: {created_count}')
        self.stdout.write(f'  - Already existed: {skipped_count}')
        self.stdout.write(f'  - Errors: {error_count}')
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Successfully fixed {created_count} reseller profiles!'
                )
            )
            self.stdout.write('Users can now create marketing links without errors.')
        else:
            self.stdout.write('\n✅ All reseller profiles are already properly configured!')
