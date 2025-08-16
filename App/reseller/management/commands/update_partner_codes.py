"""
Management command to update existing partner codes to EVOLVE format
"""
from django.core.management.base import BaseCommand
from myapp.reseller.earnings.models import Reseller
from myapp.reseller.utils import format_partner_code, generate_partner_code


class Command(BaseCommand):
    help = 'Updates all existing partner codes to use EVOLVE- prefix'

    def handle(self, *args, **options):
        resellers = Reseller.objects.all()
        updated_count = 0
        
        for reseller in resellers:
            old_code = reseller.referral_code
            
            # Check if code needs updating
            if old_code and not old_code.startswith('EVOLVE-'):
                # Try to extract user ID from old code
                if old_code.startswith('REF-') or old_code.startswith('RSL-') or old_code.startswith('RESL-'):
                    try:
                        # Extract the numeric part
                        parts = old_code.split('-')
                        if len(parts) > 1 and parts[1].isdigit():
                            user_id = int(parts[1])
                            new_code = generate_partner_code(user_id)
                        else:
                            # Use the reseller's user ID
                            new_code = generate_partner_code(reseller.user.id)
                    except:
                        # Fallback to using user ID
                        new_code = generate_partner_code(reseller.user.id)
                else:
                    # Generate new code based on user ID
                    new_code = generate_partner_code(reseller.user.id)
                
                reseller.referral_code = new_code
                reseller.save()
                updated_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated {reseller.user.username}: {old_code} -> {new_code}'
                    )
                )
            elif not old_code:
                # Generate new code if missing
                new_code = generate_partner_code(reseller.user.id)
                reseller.referral_code = new_code
                reseller.save()
                updated_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Generated code for {reseller.user.username}: {new_code}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully updated {updated_count} partner codes.'
            )
        )
