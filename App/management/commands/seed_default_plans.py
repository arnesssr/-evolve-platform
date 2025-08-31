from django.core.management.base import BaseCommand
from App.models import Plan, Feature

class Command(BaseCommand):
    help = "Seed default subscription plans if none exist (Standard, Professional)."

    def handle(self, *args, **options):
        created = 0
        if not Plan.objects.exists():
            std, _ = Plan.objects.update_or_create(
                name='Standard',
                defaults={
                    'badge': '',
                    'description': 'Great for small teams',
                    'price': 5000,          # monthly
                    'yearly_price': 51000,  # yearly (15% off approx)
                    'is_active': True,
                    'display_order': 1,
                },
            )
            pro, _ = Plan.objects.update_or_create(
                name='Professional',
                defaults={
                    'badge': 'Popular',
                    'description': 'For growing businesses',
                    'price': 8000,
                    'yearly_price': 81600,
                    'is_active': True,
                    'display_order': 2,
                },
            )
            # Seed sample features
            Feature.objects.bulk_create([
                Feature(plan=std, name='Users', value='Up to 10'),
                Feature(plan=std, name='Support', value='Email'),
                Feature(plan=pro, name='Users', value='Unlimited'),
                Feature(plan=pro, name='Support', value='Priority'),
            ])
            created = 2
        else:
            # Ensure at least one active plan
            active_exists = Plan.objects.filter(is_active=True).exists()
            if not active_exists:
                first = Plan.objects.order_by('display_order').first()
                if first:
                    first.is_active = True
                    first.save(update_fields=['is_active'])
                    created = 1
        self.stdout.write(self.style.SUCCESS(f"Seeded/activated {created} plan entries."))
