"""Sales report repository."""
from django.db.models import Count
from .base import BaseRepository
from ..models.report import SalesReport


class SalesReportRepository(BaseRepository):
    model = SalesReport

