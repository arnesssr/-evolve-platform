import json
from django.test import TestCase, Client
from django.urls import reverse
from App.models import Business


class BusinessAPICRUDTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_business(self):
        url = reverse('api_businesses_list')
        payload = {
            'business_name': 'Starter Co',
            'business_email': 'starter@co.com',
            'industry': 'Retail',
            'company_size': '1-10',
            'country': 'Kenya',
            'postal_code': '00902',
        }
        res = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data['email'], 'starter@co.com')
        self.assertTrue(Business.objects.filter(pk=data['id']).exists())

    def test_create_business_duplicate_email(self):
        Business.objects.create(
            business_name='X', business_email='dup@co.com', industry='Retail',
            company_size='1-10', country='Kenya', postal_code='00100'
        )
        url = reverse('api_businesses_list')
        payload = {
            'business_name': 'Y',
            'business_email': 'dup@co.com',
            'industry': 'Retail',
            'company_size': '1-10',
            'country': 'Kenya',
            'postal_code': '00100',
        }
        res = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_update_and_delete_business(self):
        b = Business.objects.create(
            business_name='ToUpdate', business_email='update@co.com', industry='Retail',
            company_size='1-10', country='Kenya', postal_code='00100'
        )
        detail_url = reverse('api_businesses_detail', kwargs={'pk': b.id})
        res = self.client.put(detail_url, data=json.dumps({'company_size': '11-50'}), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['company_size'], '11-50')

        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, 204)
        self.assertFalse(Business.objects.filter(pk=b.id).exists())

