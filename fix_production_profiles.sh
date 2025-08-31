#!/usr/bin/env bash
# Script to fix reseller profiles in production
# Run this after deployment to ensure all users have proper profiles

set -euo pipefail

echo "🚀 Fixing Reseller Profiles in Production..."
echo "============================================"

# Run the management command
python manage.py fix_reseller_profiles

echo ""
echo "✅ Production profiles fixed!"
echo "Users should now be able to create marketing links without errors."
