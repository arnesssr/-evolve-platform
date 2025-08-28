from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from django.utils import timezone

from App.admin.models.scheduled_report import ScheduledReport

class ReportsSchedulerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='pass', is_staff=True, is_superuser=True)

    def test_run_scheduled_reports_sets_next_run(self):
        sr = ScheduledReport.objects.create(
            report_type='revenue_summary',
            schedule='0 9 * * *',
            recipients=['a@example.com'],
            format='pdf',
            active=True,
            created_by=self.user,
        )
        # Initially, next_run_at should be None
        self.assertIsNone(sr.next_run_at)

        # Run command
        call_command('run_scheduled_reports')

        sr.refresh_from_db()
        self.assertIsNotNone(sr.last_run_at)
        self.assertIsNotNone(sr.next_run_at)
        self.assertTrue(sr.active)

