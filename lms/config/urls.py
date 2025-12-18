"""
URL configuration for LMS project - Clean Architecture version.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .admin import lms_admin_site

urlpatterns = [
    path('admin/', lms_admin_site.urls),
    
    # API v1
    path('api/v1/', include('src.presentation.api.v1.urls')),
    
    # DRF browsable API auth
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

