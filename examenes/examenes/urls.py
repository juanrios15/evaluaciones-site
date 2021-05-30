import debug_toolbar

from django.contrib import admin
from django.urls import path, re_path,include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap

from apps.users.sitemap import EvaluacionesSitemap, Sitemap

sitemaps = {
    'site': Sitemap(['users_app:inicio']),
    'evaluaciones': EvaluacionesSitemap
}

urlpatterns_sitemap = [
    path('sitemap.xml', sitemap,{'sitemaps':sitemaps},
    name='django.contrib.sitemaps.views,sitemap')

]

urlpatterns_main = [
    path('admin/', admin.site.urls),
    re_path('',include('apps.users.urls')),
    re_path('',include('apps.evaluaciones.urls')),
    re_path('',include('apps.intentos.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns_main + urlpatterns_sitemap
#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
