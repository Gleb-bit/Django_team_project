# Модуль для работы с кешами
from django.contrib.auth.models import User
from django.core.cache import cache
from loguru import logger

from main.models import Shop, Product
from marketplace.settings import CATEGORIES_CACHE_KEY_TEMPLATE, SHOPS_CACHE_KEY_TEMPLATE, BANNERS_CACHE_KEY, \
    PRODUCT_CACHE_KEY_TEMPLATE


def delete_categories_cache() -> None:
    """Метод для сброса кешей категорий"""

    logger.debug('Сработал delete_categories_cache')
    usernames = User.objects.values_list("username", flat=True)
    for username in usernames:
        cache.delete(CATEGORIES_CACHE_KEY_TEMPLATE.format(username))


def delete_shops_cache():
    """Метод для сброса кешей продавцов"""

    logger.debug(f'Сработал delete_shops_cache')
    shop_ids = Shop.objects.values_list("id", flat=True)
    for shop_id in shop_ids:
        cache.delete(SHOPS_CACHE_KEY_TEMPLATE.format(shop_id))


def delete_banners_cache():
    """Метод для сброса кешей баннеров"""

    logger.debug('Сработал delete_banners_cache')
    cache.delete(BANNERS_CACHE_KEY)


def delete_catalog_cache():
    """Метод для сброса кешей баннеров"""

    logger.debug('Сработал delete_catalog_cache')
    cache.clear()


def delete_product_cache():
    """Метод для сброса кешей баннеров"""

    logger.debug('Сработал delete_product_cache')
    slugs = Product.objects.values_list("slug", flat=True)
    for slug in slugs:
        cache.delete(PRODUCT_CACHE_KEY_TEMPLATE.format(slug))

