from typing import Dict, Any
from App.models import Business


def serialize_business_list_item(b: Business) -> Dict[str, Any]:
    return {
        'id': b.id,
        'name': b.business_name,
        'email': b.business_email,
        'industry': b.industry,
        'company_size': b.company_size,
        'country': b.country,
    }


def serialize_business_detail(b: Business) -> Dict[str, Any]:
    return {
        'id': b.id,
        'name': b.business_name,
        'email': b.business_email,
        'industry': b.industry,
        'company_size': b.company_size,
        'country': b.country,
        'postal_code': b.postal_code,
    }

