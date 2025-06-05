from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api.views import landing_page

urlpatterns = [
    path('', landing_page, name='landing-page'),  # Beautiful landing page at root
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # Your API endpoints
]

# Serve static and media files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)