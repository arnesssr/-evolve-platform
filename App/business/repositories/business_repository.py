from typing import Optional, Tuple
from django.db.models import Q, QuerySet

from App.models import Business


class BusinessRepository:
    """Data access for Business domain using the existing App.models.Business model."""

    ALLOWED_FIELDS = {
        'business_name', 'business_email', 'industry', 'company_size', 'country', 'postal_code'
    }

    def base_queryset(self) -> QuerySet:
        return Business.objects.all()

    def search(
        self,
        q: Optional[str] = None,
        industry: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> QuerySet:
        qs = self.base_queryset()
        if q:
            qs = qs.filter(
                Q(business_name__icontains=q)
                | Q(business_email__icontains=q)
            )
        if industry:
            qs = qs.filter(industry=industry)
        # NOTE: created_at filters can be added once needs are defined; using alphabetical for stability.
        return qs.order_by('business_name')

    def get_by_id(self, pk: int) -> Business:
        return self.base_queryset().get(pk=pk)

    def create(self, data: dict) -> Business:
        payload = {k: v for k, v in data.items() if k in self.ALLOWED_FIELDS}
        return Business.objects.create(**payload)

    def update(self, instance: Business, data: dict) -> Business:
        for k, v in data.items():
            if k in self.ALLOWED_FIELDS and v is not None:
                setattr(instance, k, v)
        instance.save()
        return instance

    def delete(self, pk: int) -> None:
        obj = self.get_by_id(pk)
        obj.delete()

