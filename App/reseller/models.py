"""Aggregate reseller models so Django can discover nested subpackages.
This file imports models from submodules (earnings, sales, marketing, settings) to register them with Django.
"""
# Earnings models
from .earnings.models import *  # noqa: F401,F403
# Sales models
from .sales.models import *  # noqa: F401,F403
# Marketing models
from .marketing.models import *  # noqa: F401,F403
# Settings models
from .settings.models import *  # noqa: F401,F403

