from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('App.urls')),
    path('admin/', admin.site.urls),  # Django default admin
    # Your custom admin is available at /platform/admin/
]
