#!/usr/bin/env python
"""
Fix users without UserProfile to prevent redirect to register page after login.
This script creates default UserProfiles for users who don't have them.
"""
import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from App.models import UserProfile

def fix_missing_profiles():
    """
    Create UserProfiles for users who don't have them.
    """
    print("🔧 Fixing Missing UserProfiles")
    print("=" * 50)
    
    users_without_profiles = []
    users_fixed = []
    
    # Find all users without profiles
    for user in User.objects.all():
        try:
            UserProfile.objects.get(user=user)
            print(f"✅ {user.email} - Profile exists")
        except UserProfile.DoesNotExist:
            users_without_profiles.append(user)
            print(f"❌ {user.email} - Missing profile")
    
    if not users_without_profiles:
        print("\n🎉 All users already have profiles!")
        return
    
    print(f"\n📝 Found {len(users_without_profiles)} users without profiles")
    print("Creating default profiles...")
    
    for user in users_without_profiles:
        try:
            # Determine default role based on email patterns or other logic
            if 'admin' in user.email.lower() or 'super' in user.email.lower():
                default_role = 'admin'
            elif any(keyword in user.email.lower() for keyword in ['business', 'company', 'corp']):
                default_role = 'business_owner'
            else:
                default_role = 'reseller'
            
            # Create profile with defaults
            profile = UserProfile.objects.create(
                user=user,
                phone='+254700000000',  # Default phone (user can update later)
                role=default_role,
                industry='Other'
            )
            
            users_fixed.append((user, profile))
            print(f"✅ Created profile for {user.email} - Role: {profile.role}")
            
        except Exception as e:
            print(f"❌ Failed to create profile for {user.email}: {str(e)}")
    
    print(f"\n📊 Summary:")
    print(f"- Users fixed: {len(users_fixed)}")
    print(f"- Total users now with profiles: {UserProfile.objects.count()}")
    
    if users_fixed:
        print(f"\n✅ Successfully fixed login redirect issue for {len(users_fixed)} users!")
        print("These users can now log in without being redirected to the register page.")
        
        print("\n📝 Profile assignments:")
        for user, profile in users_fixed:
            print(f"   - {user.email}: {profile.role}")
            
        print("\n💡 Users can update their phone numbers and other details after logging in.")

if __name__ == "__main__":
    fix_missing_profiles()
