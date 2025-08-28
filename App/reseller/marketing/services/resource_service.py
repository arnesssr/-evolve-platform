"""Marketing Resource service."""
from .base import BaseService
from App.reseller.marketing.repositories import MarketingResourceRepository


class MarketingResourceService(BaseService):
    def __init__(self):
        super().__init__()
        self.repo = MarketingResourceRepository()

    def list_resources(self):
        return self.repo.list_all()

