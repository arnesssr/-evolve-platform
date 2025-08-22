# Optional API scaffolding for admin resellers
# Simple JSON APIs without DRF for now
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from App.admin.services.resellers_service import AdminResellerService
from App.admin.forms.resellers import ResellerFilterForm

class ResellersListAPI(View):
    def get(self, request):
        form = ResellerFilterForm(request.GET)
        if not form.is_valid():
            return HttpResponseBadRequest('Invalid filters')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 25))
        svc = AdminResellerService()
        rows, total = svc.list_resellers(form.cleaned_data, page=page, page_size=page_size)
        return JsonResponse({'results': rows, 'total': total})

class ResellerDetailAPI(View):
    def get(self, request, reseller_id: int):
        svc = AdminResellerService()
        data = svc.get_reseller_detail(reseller_id)
        return JsonResponse(data)

class ResellerStatsAPI(View):
    def get(self, request, reseller_id: int):
        svc = AdminResellerService()
        series = svc.get_chart_series(reseller_id)
        return JsonResponse({'series': series})

