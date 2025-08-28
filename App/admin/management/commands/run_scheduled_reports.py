from django.core.management.base import BaseCommand
from django.utils import timezone

from App.admin.models.scheduled_report import ScheduledReport
from App.admin.services.scheduler_service import compute_next_run
from App.admin.services.audit_service import AuditService

class Command(BaseCommand):
    help = "Run due scheduled reports and compute next runs. Intended to be invoked by OS scheduler (cron/Task Scheduler)."

    def handle(self, *args, **options):
        now = timezone.now()
        audit = AuditService()
        due = ScheduledReport.objects.filter(active=True).filter(
            next_run_at__isnull=True
        ) | ScheduledReport.objects.filter(active=True, next_run_at__lte=now)

        count = 0
        for sched in due.order_by('next_run_at', 'created_at'):
            # Mark as run
            sched.last_run_at = now
            # Compute next run (use UTC naive time for cron calc; then localize to timezone)
            next_dt = compute_next_run(sched.schedule, now.utcnow())
            if next_dt is not None:
                # Assume next_run_at is naive UTC; convert to aware using current timezone
                sched.next_run_at = timezone.make_aware(next_dt, timezone.get_current_timezone())
            else:
                # If cannot compute, deactivate to avoid tight loops
                sched.active = False
            sched.save(update_fields=['last_run_at', 'next_run_at', 'active'])

            audit.log(
                action='report_schedule_run',
                actor_id=(sched.created_by_id or None),
                target_type='scheduled_report',
                target_id=sched.id,
                details={
                    'report_type': sched.report_type,
                    'schedule': sched.schedule,
                    'next_run_at': sched.next_run_at.isoformat() if sched.next_run_at else None,
                }
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Processed {count} scheduled report(s) at {now.isoformat()}"))

