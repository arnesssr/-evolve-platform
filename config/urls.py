from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('App.urls')),
    path('admin/', admin.site.urls),  # Django default admin
    # Your custom admin is available at /platform/admin/
]

# Serve static files in production if WhiteNoise fails
# This is a fallback - WhiteNoise should handle this automatically
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
