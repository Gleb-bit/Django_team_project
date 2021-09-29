# Модуль для работы с продуктами для сравнения
import random
from dataclasses import dataclass
from typing import List

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from loguru import logger

from compare.models import CompareProduct
from main.models import Product
from services.user_services import handle_anonymous


COMPARE_PRODUCTS_PREVIEW_COUNT = 3


@dataclass
class CompareRow:
    """Класс для отображения строк характеристик на странице сравнения"""
    characteristic_name: str  # название характиристики
    product_characteristic_values: List[str]  # список значений характеристик товаров
    hide: bool = False  # отличаются ли значения характирискик товаров, нужен для корректной работы checkbox
    # Только различающиеся характеристики на странице сравнения


def get_compare_products_count(user: User) -> int:
    """Функция получения количество товаров в списке сравнения"""

    return len(get_compare_products(user=user))


@handle_anonymous
def add_product_to_compare(product_id: int, user: User) -> None:
    """
    Метод для добавления товара product в список сравнения для пользователя user.
    Если товар уже есть в списке сравнения то добавления не происходит
    Важно: параметр user должен передаваться как именованный
    """

    compare_products = get_compare_products(user=user)
    if product_id not in [product.product.id for product in compare_products]:
        CompareProduct.objects.create(product=Product.objects.get(id=product_id), user=user)
        logger.debug(f"Пользователь '{user}' добавил продукт '{product_id}' в список сравнения")


@handle_anonymous
def remove_product_from_compare(product_id: int, user: User) -> None:
    """
    Метод для удаления товара product из списка сравнения пользователя user
    Важно: параметр user должен передаваться как именованный
    """

    CompareProduct.objects.filter(product=product_id, user=user).delete()
    logger.debug(f"Пользователь '{user}' удалил продукт '{product_id}' из списка сравнения")


@handle_anonymous
def get_compare_products(user: User) -> List[CompareProduct]:
    """
    Функция для получения товаров в сравнении у пользователя user
    Важно: параметр user должен передаваться как именованный
    """

    return CompareProduct.objects.filter(user=user).order_by("date_added")[:COMPARE_PRODUCTS_PREVIEW_COUNT]


@handle_anonymous
def get_compare_products_characteristics(user: User) -> List[CompareRow]:
    """
    Функция для получения характеристик товаров отображаемых на странице сравнения
    Важно: параметр user должен передаваться как именованный
    """

    compare_products = get_compare_products(user=user)
    if not compare_products:
        return []
    all_products_characteristics = _get_all_products_characteristics(compare_products)
    common_characteristics = _get_common_characteristics(all_products_characteristics)
    compare_rows = _calc_compare_rows(compare_products=compare_products, common_characteristics=common_characteristics)
    return compare_rows


def _get_common_characteristics(all_products_characteristics: List[List[str]]) -> List[str]:
    """Функция для получения общих характеристик товаров"""

    common_characteristics = all_products_characteristics[0]
    for index in range(1, len(all_products_characteristics)):
        common_characteristics = [item for item in common_characteristics if item in all_products_characteristics[index]]

    return common_characteristics


def _get_all_products_characteristics(compare_products: List[CompareProduct]) -> List[List[str]]:
    """
    Функция для получения всех характеристик товаров из compare_products.
    Возвращает список списков названий характеристик
    """

    all_product_characteristics = []
    for compare_product in compare_products:
        current_characteristics = [product_characteristic.characteristic.name for product_characteristic
                                   in compare_product.product.characteristics.all()]
        all_product_characteristics.append(current_characteristics)

    return all_product_characteristics


def _calc_compare_rows(compare_products: List[CompareProduct], common_characteristics: List[str]) -> List[CompareRow]:
    """Функция для вычисления строк характеристик для отображения значений характеристик на странице сравнения"""

    compare_rows = []
    for characteristic_name in common_characteristics:
        product_characteristic_values = []
        for compare_product in compare_products:
            product_characteristic_value = compare_product.product.characteristics.\
                filter(characteristic__name=characteristic_name).values_list('value', flat=True)[0]
            product_characteristic_values.append(product_characteristic_value)
        compare_rows.append(CompareRow(characteristic_name=characteristic_name,
                                       product_characteristic_values=product_characteristic_values,
                                       hide=len(set(product_characteristic_values)) == 1)
                            )

    return compare_rows


def get_philosophical_phrase():
    """Функция для получения философской фразы, когда у товаров нет общих характеристик"""

    phrases = [
        _("The wolf is not a sheep's comrade"),
        _("Can't compare incomparable"),
        _("These products have nothing in common"),
        _("A circle and a square have zero common sides"),
        _("No common characteristics"),
        _("They are like sea and mountain"),
        _("It is difficult to compare what cannot be compared"),
        _("They are like nitrogen and calcium - nothing in common"),
        _("Like a cat and a dog"),
    ]

    return random.choice(phrases)
