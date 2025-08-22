from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse

from App.admin.forms.resellers import (
    ResellerFilterForm,
    ResellerCreateForm,
    ResellerEditForm,
    ResellerBulkActionForm,
    SuspendForm,
    PayoutForm,
    MessageForm,
)
from App.admin.services.resellers_service import AdminResellerService
from App.admin.permissions import AdminRequiredMixin  # assume this exists or will be added


class AdminResellerListView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'dashboards/admin/pages/resellers/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ResellerFilterForm(self.request.GET)
        form.is_valid()  # normalize filters; ignore errors, show empty/defaults
        svc = AdminResellerService()
        context['metrics'] = svc.compute_metrics()
        page = int(self.request.GET.get('page', 1))
        page_size = int(self.request.GET.get('page_size', 25))
        context['resellers'], context['total_count'] = svc.list_resellers(form.cleaned_data, page=page, page_size=page_size)
        return context


class AdminResellerDetailView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'dashboards/admin/pages/resellers/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reseller_id = kwargs.get('reseller_id')
        svc = AdminResellerService()
        context['reseller'] = svc.get_reseller_detail(reseller_id)
        return context


class AdminResellerExportView(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request):
        form = ResellerFilterForm(request.GET)
        if not form.is_valid():
            return HttpResponseBadRequest('Invalid filters')
        svc = AdminResellerService()
        rows = svc.export_rows(form.cleaned_data)
        # naive CSV for scaffold; replace with utils exporter if present
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="resellers.csv"'
        response.write('id,name,email,company,commission_tier,total_earnings,sales_count,status,joined\n')
        for r in rows:
            response.write(f"{r.get('id','')},{r.get('name','')},{r.get('email','')},{r.get('company','')},{r.get('commission_tier','')},{r.get('total_earnings','')},{r.get('sales_count','')},{r.get('status','')},{r.get('joined','')}\n")
        return response


class AdminResellerBulkActionView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request):
        form = ResellerBulkActionForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest('Invalid bulk action')
        svc = AdminResellerService()
        result = svc.handle_bulk_action(form.cleaned_data)
        # Redirect back to list for scaffold
        return redirect(reverse('platform_admin:resellers-list'))


class AdminResellerCreateView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request):
        form = ResellerCreateForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest('Invalid create form')
        svc = AdminResellerService()
        reseller_id = svc.create_reseller(form.cleaned_data)
        return redirect(reverse('platform_admin:resellers-detail', kwargs={'reseller_id': reseller_id}))


class AdminResellerEditView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, reseller_id):
        form = ResellerEditForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest('Invalid edit form')
        svc = AdminResellerService()
        svc.update_reseller(reseller_id, form.cleaned_data)
        return redirect(reverse('platform_admin:resellers-detail', kwargs={'reseller_id': reseller_id}))


class AdminResellerSuspendView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, reseller_id):
        form = SuspendForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest('Invalid suspend form')
        reason = form.cleaned_data.get('reason')
        svc = AdminResellerService()
        svc.suspend_reseller(reseller_id, reason=reason)
        return redirect(reverse('platform_admin:resellers-detail', kwargs={'reseller_id': reseller_id}))


class AdminResellerResumeView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, reseller_id):
        svc = AdminResellerService()
        svc.resume_reseller(reseller_id)
        return redirect(reverse('platform_admin:resellers-detail', kwargs={'reseller_id': reseller_id}))


class AdminResellerPayoutView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, reseller_id):
        form = PayoutForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest('Invalid payout form')
        svc = AdminResellerService()
        svc.process_payout(reseller_id, form.cleaned_data)
        return redirect(reverse('platform_admin:resellers-detail', kwargs={'reseller_id': reseller_id}))


class AdminResellerMessageView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request):
        form = MessageForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest('Invalid message form')
        svc = AdminResellerService()
        svc.send_message(form.cleaned_data.get('reseller_ids'), form.cleaned_data.get('channel'), form.cleaned_data)
        return redirect(reverse('platform_admin:resellers-list'))


class AdminResellerStatsView(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request, reseller_id):
        svc = AdminResellerService()
        series = svc.get_chart_series(reseller_id)
        return JsonResponse({'series': series})

