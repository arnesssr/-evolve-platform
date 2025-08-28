from typing import Dict
from App.admin.services.settings_service import SettingsService


CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'KES': 'KSh'
}


def platform_settings(request) -> Dict:
    general = SettingsService.get_section('general')
    currency = general.get('default_currency', 'USD')
    language = general.get('default_language', 'en')
    symbol = CURRENCY_SYMBOLS.get(currency, '$')
    return {
        'PLATFORM_SETTINGS': {
            'default_currency': currency,
            'currency_symbol': symbol,
            'default_language': language,
            'platform_name': general.get('platform_name', 'Evolve Platform'),
            'platform_url': general.get('platform_url', ''),
            'support_email': general.get('support_email', ''),
            'timezone': general.get('timezone', 'UTC'),
        }
    }
