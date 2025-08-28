from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
import json
from decimal import Decimal

from App.models import Product

class AdminProductCreateAPI(View):
    """
    Create a product from Quick Create modal.
    Expects JSON body with fields:
    - name (str, required)
    - sku (str, optional)
    - description (str, optional)
    - category (str, optional)
    - vendor (str, optional)
    - price (number, required)
    - commission_rate (number, optional)
    - active (bool, optional)
    - featured (bool, optional)
    """

    def post(self, request):
        try:
            payload = json.loads(request.body.decode('utf-8')) if request.body else {}
        except Exception:
            return HttpResponseBadRequest('Invalid JSON body')

        name = (payload.get('name') or '').strip()
        price = payload.get('price')
        if not name:
            return HttpResponseBadRequest('name is required')
        if price is None:
            return HttpResponseBadRequest('price is required')

        # Normalize numbers
        try:
            price = Decimal(str(price))
        except Exception:
            return HttpResponseBadRequest('price must be a number')

        commission_rate = payload.get('commission_rate')
        if commission_rate is not None and commission_rate != '':
            try:
                commission_rate = Decimal(str(commission_rate))
            except Exception:
                return HttpResponseBadRequest('commission_rate must be a number')
        else:
            commission_rate = None

        status = 'active' if payload.get('active') else 'draft'

        p = Product.objects.create(
            name=name,
            sku=(payload.get('sku') or '').strip() or None,
            description=payload.get('description') or '',
            category=payload.get('category') or '',
            vendor=payload.get('vendor') or '',
            price=price,
            commission_rate=commission_rate,
            status=status,
            is_featured=bool(payload.get('featured')),
        )

        return JsonResponse({'success': True, 'id': p.id})


class AdminProductDetailAPI(View):
    def get(self, request, product_id: int):
        try:
            p = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return HttpResponseBadRequest('Product not found')
        data = {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'category': p.category,
            'vendor': p.vendor,
            'price': float(p.price),
            'price_display': f"${p.price:.2f}",
            'commission_rate': float(p.commission_rate) if p.commission_rate is not None else None,
            'commission_rate_display': (f"{p.commission_rate}%" if p.commission_rate is not None else '—'),
            'status': p.status,
            'sales_count': p.sales_count,
            'created': p.created_at.isoformat() if p.created_at else None,
            'created_display': p.created_at.strftime('%b %d, %Y') if p.created_at else None,
        }
        return JsonResponse({'success': True, 'data': data})

