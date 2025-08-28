"""Marketing resource repository."""
from .base import BaseRepository
from App.reseller.marketing.models import MarketingResource


class MarketingResourceRepository(BaseRepository):
    model = MarketingResource

    def list_all(self):
        return self.get_all()

