from django.core.cache import cache
from django.db.models import Prefetch
from django.views.generic.base import ContextMixin
from loguru import logger

from main.models import Category, Banner
from marketplace.settings import BANNERS_COUNT, CATEGORIES_CACHE_KEY_TEMPLATE, BANNERS_CACHE_KEY
from services.cart_services import get_user_cart_total_amount, get_user_cart_cost
from services.compare_services import get_compare_products_count
from services.settings_services import get_categories_cache_timeout, get_banners_cache_timeout


class CategoriesContextMixin(ContextMixin):
    """ Миксин для добавление в контекст набора категорий """
    def get_context_data(self, **kwargs):
        logger.debug(f'Получение контекста набора категорий')
        context = super(CategoriesContextMixin, self).get_context_data(**kwargs)
        categories_key = CATEGORIES_CACHE_KEY_TEMPLATE.format(self.request.user.username)
        categories = Category.objects.filter(parent_category=None, is_active=True).prefetch_related(
            Prefetch('children_categories',
                     queryset=Category.objects.filter(is_active=True).order_by('sort_index'))) \
            .order_by('sort_index')
        categories = cache.get_or_set(categories_key, categories, get_categories_cache_timeout())
        context['categories'] = categories
        return context


class CartContextMixin(ContextMixin):
    """ Миксин для добавления в контекст сведений о корзине """
    def get_context_data(self, **kwargs):
        logger.debug(f'Получение контекста сведений о корзине')
        context = super(CartContextMixin, self).get_context_data(**kwargs)
        context['cart_size'] = get_user_cart_total_amount(user=self.request.user)
        context['cart_cost'] = get_user_cart_cost(user=self.request.user)
        return context


class BannersContextMixin(ContextMixin):
    """Mixin для баннеров на главной странице"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        banners = Banner.objects.filter(is_active=True).order_by('?')[:BANNERS_COUNT]
        banners = cache.get_or_set(BANNERS_CACHE_KEY, banners, get_banners_cache_timeout())
        context['banners'] = banners
        return context


class CompareContextMixin(ContextMixin):
    """Mixin для количества товаров в сравнении"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['compare_count'] = get_compare_products_count(self.request.user)

        return context


class BaseMixin(CategoriesContextMixin, CompareContextMixin, CartContextMixin):
    """Mixin информации для всех страниц"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return context
