from typing import Any, Dict
import json
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.csrf import csrf_exempt

from App.business.forms.filter import BusinessFilterForm
from App.business.forms.create import BusinessCreateForm
from App.business.forms.update import BusinessUpdateForm
from App.business.services.business_service import BusinessService
from App.business.repositories.business_repository import BusinessRepository


@csrf_exempt
@require_http_methods(["GET", "POST"])
def businesses_collection(request):
    svc = BusinessService()
    if request.method == "GET":
        form = BusinessFilterForm(request.GET)
        if not form.is_valid():
            return JsonResponse({'error': 'Invalid parameters', 'details': form.errors}, status=400)
        payload = svc.list_businesses(form.cleaned_data)
        return JsonResponse(payload)
    # POST
    try:
        body = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    form = BusinessCreateForm(body)
    if not form.is_valid():
        return JsonResponse({'error': 'Invalid data', 'details': form.errors}, status=400)
    data = svc.create_business(form.cleaned_data)
    return JsonResponse(data, status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def business_detail(request, pk: int):
    svc = BusinessService()
    if request.method == "GET":
        try:
            data = svc.get_business(pk)
            return JsonResponse(data)
        except Exception:
            raise Http404
    if request.method in ("PUT", "PATCH"):
        try:
            instance = BusinessRepository().get_by_id(pk)
        except Exception:
            raise Http404
        try:
            body = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
        form = BusinessUpdateForm(body, instance=instance)
        if not form.is_valid():
            return JsonResponse({'error': 'Invalid data', 'details': form.errors}, status=400)
        data = svc.update_business(pk, form.cleaned_data)
        return JsonResponse(data)
    # DELETE
    try:
        svc.delete_business(pk)
        return HttpResponse(status=204)
    except Exception:
        raise Http404

