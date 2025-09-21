from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from gamenews.views import About

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', About.as_view(), name='about'),
    path('', include('gamenews.urls')),
    path('user/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
