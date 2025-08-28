"""Marketing Tool service."""
from .base import BaseService
from App.reseller.marketing.repositories import MarketingToolRepository


class MarketingToolService(BaseService):
    def __init__(self):
        super().__init__()
        self.repo = MarketingToolRepository()

    def list_tools(self):
        return self.repo.list_active()

