"""Marketing Link service."""
from .base import BaseService
from App.reseller.marketing.repositories import MarketingLinkRepository


class MarketingLinkService(BaseService):
    def __init__(self):
        super().__init__()
        self.repo = MarketingLinkRepository()

    def list_links(self, reseller):
        return self.repo.list_for_reseller(reseller)

    def create_link(self, reseller, data):
        return self.repo.create(reseller=reseller, **data)

