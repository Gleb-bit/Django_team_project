from django.core.cache import cache
from django.views.generic import ListView, DetailView

from main.models import Shop
from marketplace.settings import SHOPS_CACHE_KEY_TEMPLATE
from marketplace.views import BaseMixin
from services.settings_services import get_shops_cache_timeout


class ShopListView(BaseMixin, ListView):
    """Представление для списка продавцов"""
    model = Shop
    queryset = Shop.objects.all()
    context_object_name = 'shop_list'
    template_name = 'shop/shop_list.html'


class ShopDetailView(BaseMixin, DetailView):
    """Представление для детальной информации о продавце"""
    model = Shop
    queryset = Shop.objects.all()
    context_object_name = 'shop'
    template_name = 'shop/shop_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        shop_key = SHOPS_CACHE_KEY_TEMPLATE.format(self.get_object().id)
        context[self.context_object_name] = cache.get_or_set(shop_key, self.get_object(), get_shops_cache_timeout())

        return context
