from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone

class ReportsApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='pass')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)

    def test_preview_generate_and_schedule(self):
        start = timezone.now().date().strftime('%Y-%m-%d')
        end = start

        # Preview
        pr = self.client.post(
            '/platform/admin/api/v1/finance/reports/preview/',
            data={
                'type': 'revenue_summary',
                'parameters': {
                    'start_date': f'{start}T00:00:00Z',
                    'end_date': f'{end}T23:59:59Z',
                    'format': 'pdf'
                }
            },
            content_type='application/json'
        )
        self.assertEqual(pr.status_code, 200, pr.content)
        self.assertTrue(pr.json().get('success'))

        # Generate
        gr = self.client.post(
            '/platform/admin/api/v1/finance/reports/generate/',
            data={
                'type': 'revenue_summary',
                'parameters': {
                    'start_date': f'{start}T00:00:00Z',
                    'end_date': f'{end}T23:59:59Z',
                    'format': 'pdf'
                }
            },
            content_type='application/json'
        )
        self.assertEqual(gr.status_code, 200, gr.content)
        gd = gr.json()
        self.assertTrue(gd.get('success'))
        self.assertIn('filename', gd['data'])
        self.assertIn('/platform/admin/api/v1/finance/reports/download/', gd['data']['download_url'])

        # Schedule
        sr = self.client.post(
            '/platform/admin/api/v1/finance/reports/schedule/',
            data={
                'report_type': 'revenue_summary',
                'schedule': '0 9 1 * *',
                'recipients': ['admin@example.com'],
                'format': 'pdf',
                'active': True
            },
            content_type='application/json'
        )
        self.assertEqual(sr.status_code, 200, sr.content)
        self.assertTrue(sr.json().get('success'))
        self.assertIn('schedule_id', sr.json()['data'])

        # List schedules
        lr = self.client.get('/platform/admin/api/v1/finance/reports/schedule/')
        self.assertEqual(lr.status_code, 200, lr.content)
        self.assertTrue(lr.json().get('success'))
        self.assertGreaterEqual(lr.json()['data']['total_count'], 1)

