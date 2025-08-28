from typing import Dict, Any
from django.core.cache import cache
from django.utils import timezone
from App.admin.models import PlatformSettings

CACHE_KEY = 'platform_settings_v1'
CACHE_TTL = 60  # 1 minute cache for reads


class SettingsService:
    @staticmethod
    def _get_settings_obj() -> PlatformSettings:
        return PlatformSettings.get_solo()

    @staticmethod
    def get_all() -> Dict[str, Any]:
        data = cache.get(CACHE_KEY)
        if data is None:
            obj = SettingsService._get_settings_obj()
            data = {
                'general': obj.general or {},
                'security': obj.security or {},
                'notifications': obj.notifications or {},
                'integrations': obj.integrations or {},
                'updated_at': obj.updated_at.isoformat() if obj.updated_at else None,
            }
            cache.set(CACHE_KEY, data, CACHE_TTL)
        return data

    @staticmethod
    def get_section(section: str) -> Dict[str, Any]:
        all_data = SettingsService.get_all()
        return all_data.get(section, {})

    @staticmethod
    def update_section(section: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        obj = SettingsService._get_settings_obj()
        if section == 'general':
            obj.general = {**(obj.general or {}), **payload}
        elif section == 'security':
            obj.security = {**(obj.security or {}), **payload}
        elif section == 'notifications':
            obj.notifications = {**(obj.notifications or {}), **payload}
        elif section == 'integrations':
            obj.integrations = {**(obj.integrations or {}), **payload}
        else:
            raise ValueError('Unknown settings section')
        obj.save(update_fields=[section, 'updated_at'])
        cache.delete(CACHE_KEY)
        return SettingsService.get_section(section)
