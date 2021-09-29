from django.contrib.auth.models import User, AnonymousUser
from django.db.models import QuerySet, Max, Avg, F
from django.utils import timezone
from loguru import logger

from main.models import RecentProduct, Product, Discount, Warehouse, Cart
from marketplace.settings import RECENT_PRODUCT_DISPLAY_COUNT


class RecentProductsEngine:

    @staticmethod
    def get_recent_products_to_display(user: User, number_products: int = RECENT_PRODUCT_DISPLAY_COUNT) \
            -> QuerySet[RecentProduct]:
        """
        Функция для получения списка последних просмотренных товаров для отображения.
        Если не задан параметр number_products, то возращается количество товара заданное в константе
        RECENT_PRODUCT_DISPLAY_COUNT в файле настроек
        """

        return user.recent_products.order_by('-tm')[:number_products]

    @staticmethod
    def get_recent_products_len(user: User) -> int:
        """Функция получения количества просмотренных товаров пользователем user"""

        return user.recent_products.count()

    @staticmethod
    def remove_recent_product(user: User, product: Product):
        """Метод для удаления товара из списка просмотренных"""

        product_to_delete = user.recent_products.filter(product=product.id)
        product_to_delete.delete()

    @classmethod
    def add_recent_product(cls, user: User, product: Product):
        """
        Метод для добавления товара product в список просмотренного у пользователя user.
        Если пользователь аноним, то ничего не происходит
        Если товар уже есть в списке просмотренного, то у этого товара обновляется дата добавления
        """

        if isinstance(user, AnonymousUser):
            return

        if RecentProductsEngine.is_product_in_recent_list(user=user, product=product):
            user.recent_products.filter(product=product.id).update(tm=timezone.now())
            logger.debug(f"Пользователь {user.username}, у просмотренного товара '{product.name}'"
                         f" обновлена дата просмотра")
        else:
            RecentProduct.objects.create(user=user, product=product)
            logger.debug(f"Пользователь {user.username}, добавлен товар '{product.name}' в список просмотренного ")

    @classmethod
    def is_product_in_recent_list(cls, user: User, product: Product) -> bool:
        """Функция проверяет есть ли товар product в списке просмотенного у пользователя user"""

        all_recent_products = [recent_product.product for recent_product in user.recent_products.all()]

        return product in all_recent_products
