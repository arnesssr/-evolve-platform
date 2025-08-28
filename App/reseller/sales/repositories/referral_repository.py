"""Referral repository."""
from django.db.models import Count
from .base import BaseRepository
from ..models.referral import Referral


class ReferralRepository(BaseRepository):
    model = Referral

    def by_status(self, reseller):
        return self.filter(reseller=reseller).values('status').annotate(count=Count('id')).order_by('status')

