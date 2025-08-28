"""Settings repository and service (layered)."""
from App.reseller.settings.models import ResellerSettings


class ResellerSettingsRepository:
    def get_or_create_for_reseller(self, reseller):
        obj, _ = ResellerSettings.objects.get_or_create(reseller=reseller)
        return obj

    def update_preferences(self, reseller, preferences: dict):
        obj = self.get_or_create_for_reseller(reseller)
        obj.preferences = preferences
        obj.save(update_fields=["preferences", "updated_at"])
        return obj


class ResellerSettingsService:
    def __init__(self):
        self.repo = ResellerSettingsRepository()

    def get_preferences(self, reseller):
        return self.repo.get_or_create_for_reseller(reseller).preferences

    def update_preferences(self, reseller, preferences: dict):
        return self.repo.update_preferences(reseller, preferences)

