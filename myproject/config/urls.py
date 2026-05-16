"""
URL configuration for MyProject project.

Includes routes for:
- Django admin site
- Core application URLs (to be implemented)
- API endpoints under /api/
- Media serving in DEBUG mode
"""

from django.contrib import admin
from django.views.static import serve
from django.urls import path, include
from django.urls import re_path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin site
    path('admin/', admin.site.urls),

    # Core application URLs (placeholder)
    # Will be organized by domain in core/urls/
    path('', include('app.urls')),

    # API endpoints under /api/
    path('api/', include('app.api.urls')),
]

# Serve media files (uploads/assets under MEDIA_ROOT).
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
