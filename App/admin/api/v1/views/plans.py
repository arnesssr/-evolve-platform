from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
import json
from decimal import Decimal

from App.models import Plan

class AdminPlanCreateAPI(View):
    """
    Create a plan from Quick Create modal.
    Expects JSON body with fields:
    - name (str, required)
    - description (str, optional)
    - plan_type (str, optional) -> stored in badge
    - monthly_price (number, required) -> stored in price
    - annual_price (number, optional) -> stored in yearly_price
    - active (bool, optional) -> stored in is_active
    """

    def post(self, request):
        try:
            payload = json.loads(request.body.decode('utf-8')) if request.body else {}
        except Exception:
            return HttpResponseBadRequest('Invalid JSON body')

        name = (payload.get('name') or '').strip()
        monthly_price = payload.get('monthly_price')
        if not name:
            return HttpResponseBadRequest('name is required')
        if monthly_price is None:
            return HttpResponseBadRequest('monthly_price is required')

        # Normalize numbers
        try:
            monthly_price = Decimal(str(monthly_price))
        except Exception:
            return HttpResponseBadRequest('monthly_price must be a number')

        annual_price = payload.get('annual_price')
        if annual_price not in (None, ''):
            try:
                annual_price = Decimal(str(annual_price))
            except Exception:
                return HttpResponseBadRequest('annual_price must be a number')
        else:
            annual_price = Decimal('0.00')

        p = Plan.objects.create(
            name=name,
            badge=(payload.get('plan_type') or '').title(),
            description=payload.get('description') or '',
            price=monthly_price,
            yearly_price=annual_price,
            is_active=bool(payload.get('active', True)),
            display_order=0,
        )

        return JsonResponse({'success': True, 'id': p.id})

