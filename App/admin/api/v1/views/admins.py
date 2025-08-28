from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model

User = get_user_model()

@method_decorator(staff_member_required, name='dispatch')
class AdminsCountAPI(View):
    def get(self, request):
        count = User.objects.filter(is_staff=True).count()
        return JsonResponse({'count': count})

