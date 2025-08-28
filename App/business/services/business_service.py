from typing import Dict, Any, List
from django.core.paginator import Paginator

from App.business.repositories.business_repository import BusinessRepository


class BusinessService:
    """Orchestrates business use-cases and presentation-friendly results."""

    def __init__(self, repo: BusinessRepository | None = None) -> None:
        self.repo = repo or BusinessRepository()

    def list_businesses(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        q = (filters.get('q') or '').strip() or None
        industry = (filters.get('industry') or '').strip() or None
        page = int(filters.get('page') or 1)
        page_size = int(filters.get('page_size') or 25)

        qs = self.repo.search(q=q, industry=industry)
        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)

        results = [
            {
                'id': b.id,
                'name': b.business_name,
                'email': b.business_email,
                'industry': b.industry,
                'company_size': b.company_size,
                'country': b.country,
                'created_at': b.created_at.isoformat() if hasattr(b, 'created_at') and b.created_at else None,
            }
            for b in page_obj.object_list
        ]
        return {
            'count': paginator.count,
            'page': page_obj.number,
            'page_size': page_size,
            'results': results,
        }

    def get_business(self, pk: int) -> Dict[str, Any]:
        b = self.repo.get_by_id(pk)
        return {
            'id': b.id,
            'name': b.business_name,
            'email': b.business_email,
            'industry': b.industry,
            'company_size': b.company_size,
            'country': b.country,
            'postal_code': b.postal_code,
            'created_at': b.created_at.isoformat() if hasattr(b, 'created_at') and b.created_at else None,
        }

    def create_business(self, data: Dict[str, Any]) -> Dict[str, Any]:
        b = self.repo.create(data)
        return {
            'id': b.id,
            'name': b.business_name,
            'email': b.business_email,
            'industry': b.industry,
            'company_size': b.company_size,
            'country': b.country,
            'postal_code': b.postal_code,
        }

    def update_business(self, pk: int, data: Dict[str, Any]) -> Dict[str, Any]:
        instance = self.repo.get_by_id(pk)
        b = self.repo.update(instance, data)
        return {
            'id': b.id,
            'name': b.business_name,
            'email': b.business_email,
            'industry': b.industry,
            'company_size': b.company_size,
            'country': b.country,
            'postal_code': b.postal_code,
        }

    def delete_business(self, pk: int) -> None:
        self.repo.delete(pk)

