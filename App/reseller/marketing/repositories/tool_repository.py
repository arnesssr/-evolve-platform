"""Marketing tool repository."""
from .base import BaseRepository
from App.reseller.marketing.models import MarketingTool


class MarketingToolRepository(BaseRepository):
    model = MarketingTool

    def list_active(self):
        return self.filter(is_active=True)

