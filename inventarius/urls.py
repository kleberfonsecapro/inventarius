from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin_site import custom_admin_site

urlpatterns = [
    path('painel/', custom_admin_site.urls),
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
