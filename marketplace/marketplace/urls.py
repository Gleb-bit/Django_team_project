from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('shop/', include('shop.urls')),
    path('setting/', include('setting.urls')),
    path('compare/', include('compare.urls')),
    path('catalog/', include('catalog.urls')),
    path('private_office/', include('private_office.urls')),
    path('cart/', include('cart.urls')),
    path('ajax/', include('ajax.urls')),
    path('discount/', include('discount.urls')),
    path('import/', include('import_files.urls')),
    path('payment/', include('payment.urls')),
    path('i18n', include('django.conf.urls.i18n')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
