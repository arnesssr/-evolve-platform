"""Marketing link repository."""
from .base import BaseRepository
from App.reseller.marketing.models import MarketingLink


class MarketingLinkRepository(BaseRepository):
    model = MarketingLink

    def list_for_reseller(self, reseller):
        return self.filter(reseller=reseller, is_active=True)

