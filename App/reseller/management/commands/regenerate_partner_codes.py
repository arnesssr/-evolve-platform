"""
Management command to regenerate partner codes with unique alphanumeric format
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from myapp.reseller.earnings.models import Reseller
from myapp.reseller.utils import generate_partner_code


class Command(BaseCommand):
    help = 'Regenerates all partner codes with unique alphanumeric format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Regenerate code for specific username only',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        username = options.get('user')
        dry_run = options.get('dry_run', False)
        
        # Get resellers to update
        if username:
            resellers = Reseller.objects.filter(user__username=username)
            if not resellers.exists():
                self.stdout.write(
                    self.style.ERROR(f'No reseller found with username: {username}')
                )
                return
        else:
            resellers = Reseller.objects.all()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        updated_count = 0
        
        with transaction.atomic():
            for reseller in resellers:
                old_code = reseller.referral_code
                new_code = generate_partner_code(reseller.user.id)
                
                if not dry_run:
                    reseller.referral_code = new_code
                    reseller.save()
                
                updated_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{"Would update" if dry_run else "Updated"} {reseller.user.username}: {old_code} -> {new_code}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"Would regenerate" if dry_run else "Successfully regenerated"} {updated_count} partner codes.'
            )
        )
