from datetime import datetime

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models import QuerySet, Avg, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from loguru import logger

from marketplace.settings import CATEGORIES_CACHE_KEY_TEMPLATE, SHOPS_CACHE_KEY_TEMPLATE, BANNERS_CACHE_KEY, \
    PRODUCT_CACHE_KEY_TEMPLATE


class Category(models.Model):
    """Модель категорий товара"""

    name = models.CharField(max_length=128, verbose_name=_("Name"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))
    parent_category = models.ForeignKey(
        "Category", null=True, blank=True, on_delete=models.CASCADE,
        verbose_name=_("Parent category"), related_name="children_categories")
    sort_index = models.IntegerField(default=0, verbose_name=_("Sort index"))
    img = models.ImageField(upload_to="category_images/", verbose_name=_("Image"), null=True)

    def __str__(self):
        return self.name

    def has_subcategories(self) -> bool:
        """
        Проверка есть ли у категории дочерние категории
        :return: булево значение проверки
        """
        return True if self.children_categories.all() else False

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


@receiver(post_save, sender=Category)
def clear_categories_cache(sender, **kwargs):
    logger.debug('Сработал clear_categories_cache')
    usernames = User.objects.values_list("username", flat=True)
    for username in usernames:
        cache.delete(CATEGORIES_CACHE_KEY_TEMPLATE.format(username))


class Product(models.Model):
    """Модель товара"""

    name = models.CharField(max_length=128, verbose_name=_("Name"))
    slug = models.SlugField(null=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name=_("Category"), related_name="products")
    img = models.ImageField(upload_to="product_images/", verbose_name=_("Image"), null=True, blank=True)
    description = models.TextField(verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))
    sells = models.IntegerField(verbose_name=_("Sells"))
    released = models.DateTimeField(auto_now_add=True, verbose_name=_("Released"))
    sort_index = models.IntegerField(default=0, verbose_name=_("Sort index"))

    def __str__(self):
        return self.name

    def get_active_discounts(self) -> QuerySet['Discount']:
        """
        Получение всех активных скидок на товар
        :return: набор скидок по запросу
        """
        logger.debug(f'Получение активных скидок на товар "{self}"')
        active_discounts = Discount.objects.filter(
            Q(product=self, date_end__gt=datetime.now(), date_start__lt=datetime.now())
            | Q(product=self, date_end__gt=datetime.now(), date_start__isnull=True))
        return active_discounts

    def is_discounted(self) -> bool:
        """
        Проверка действуют ли на товар скидки
        :return: булево значение проверки
        """
        return True if self.get_active_discounts() else False

    def get_best_discount(self) -> 'Discount':
        """
        Получение максимальной скидки на товар
        :return: объект скидки
        """
        logger.debug(f'Получение максимальной скидки на товар "{self}"')
        active_discounts = self.get_active_discounts()
        return active_discounts.order_by('-percent')[0]

    def get_best_discount_percent(self) -> int:
        """
        Получение максимального значения скидки на товар
        :return: значение скидки
        """
        logger.debug(f'Получение максимального значения скидки на товар "{self}"')
        return self.get_best_discount().percent

    def get_price_by_discount(self, discount: 'Discount') -> float:
        """
        Получение цены продукта по действующей на него скидке
        :param discount: объект скидки
        :return: средняя цена на товар
        """
        logger.debug(f'Получение цены продукта "{self}" по действующей на него скидке')
        if self == discount.product:
            if discount.shop:
                warehouse = Warehouse.objects.get(product=self, shop=discount.shop)
                return warehouse.price
            else:
                return round(self.warehouse.aggregate(Avg('price'))['price__avg'], 2)
        else:
            raise ValueError('Invalid discount for this product')

    def get_discounted_price(self) -> float:
        """
        Получение цены товара со скидкой
        :return: значение цены со скидкой
        """
        logger.debug(f'Получение цены товара "{self}" со скидкой')
        discount = self.get_best_discount()
        return round(self.get_price_by_discount(discount) * (100 - discount.percent) / 100, 2)

    def get_price(self) -> float:
        """
        Получение цены на товар
        :return: значение цены
        """
        logger.debug(f'Получение цены на товар "{self}"')
        return round(self.warehouse.aggregate(Avg('price'))['price__avg'], 2)

    def get_review_count(self) -> int:
        """
        Получение количества отзывов на товар
        :return: количество отзывов
        """
        logger.debug(f'Получение количества отзывов на товар "{self}"')
        return self.reviews.count()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")


@receiver(post_save, sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    logger.debug(f'Сработал clear_product_cache')
    cache.delete(PRODUCT_CACHE_KEY_TEMPLATE.format(instance.id))


class Discount(models.Model):
    """
    Модель скидки на товар.
    Если не заполнен shop, то скидка применяется к товарам любых магазинов
    """

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Product"), related_name="discounts")
    percent = models.IntegerField(verbose_name=_("Discount percentage"))
    shop = models.ForeignKey('Shop', verbose_name=_("Shop"), on_delete=models.CASCADE, null=True, blank=True)
    date_start = models.DateTimeField(null=True, blank=True, verbose_name=_("Discount start datetime"))
    date_end = models.DateTimeField(verbose_name=_("Discount end datetime"))
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_("Discount created datetime"))

    def __str__(self):
        return f'product: {self.product.name}, percent {self.percent}, period: {self.date_start} - {self.date_end}'

    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")


@receiver(post_save, sender=Discount)
def discount_price_for_warehouse(sender, instance, **kwargs):
    logger.debug('Сработал discount_price_for_warehouse')
    warehouses = instance.product.warehouse.all()
    for warehouse in warehouses:
        if warehouse.shop == instance.shop or instance.shop is None:
            warehouse.discounted_price = round(warehouse.price * (100 - instance.percent) / 100, 2)
        else:
            warehouse.discounted_price = warehouse.price


class Shop(models.Model):
    """Модель продавца"""
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    img = models.ImageField(upload_to="shop_images/", verbose_name=_("Image"), null=True, blank=True)
    description = models.TextField(verbose_name=_("Description"))
    phone = models.CharField(max_length=30, verbose_name=_("Phone"))
    address = models.TextField(verbose_name=_("Address"))
    email = models.EmailField(verbose_name=_("Email"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Shop")
        verbose_name_plural = _("Shops")


@receiver(post_save, sender=Shop)
def clear_shop_cache(sender, instance, **kwargs):
    logger.debug(f'Сработал clear_shop_cache')
    cache.delete(SHOPS_CACHE_KEY_TEMPLATE.format(instance.id))


class Warehouse(models.Model):
    """Модель склада продавца"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Product"), related_name="warehouse")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name=_("Shop"), related_name="warehouse")
    price = models.FloatField(verbose_name=_("Product price"))
    discounted_price = models.FloatField(verbose_name=_("Discounted price"))
    amount = models.PositiveIntegerField(verbose_name=_("Product amount"))
    free_shipping = models.BooleanField(verbose_name=_("Free shipping"), default=False)

    def __str__(self):
        return f'product: {self.product.name}, shop: {self.shop.name}, price: {self.price}, amount {self.amount}'

    class Meta:
        verbose_name = _("Warehouse")
        verbose_name_plural = _("Warehouses")


@receiver(post_save, sender=Warehouse)
def warehouse_discounted_price(sender, instance, **kwargs):
    logger.debug('Сработал warehouse_discounted_price')
    if instance.product.is_discounted():
        discount = instance.product.get_best_discount()
        if discount.shop == instance.shop or discount.shop is None:
            instance.discounted_price = round(instance.price * (100 - discount.percent) / 100, 2)
        else:
            instance.discounted_price = instance.price
    else:
        instance.discounted_price = instance.price


class Banner(models.Model):
    """Модель баннера"""

    title = models.CharField(max_length=128, verbose_name=_("Title"))
    text = models.TextField(verbose_name=_("Content"))
    link = models.URLField(blank=True, verbose_name=_("Link"))
    image = models.ImageField(upload_to='banner_images', verbose_name=_("Image"), null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))

    def __str__(self):
        return f'{self.title};{self.text}; active:{self.is_active}'

    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Banners")


@receiver(post_save, sender=Banner)
def clear_banners_cache(sender, **kwargs):
    logger.debug('Сработал clear_banners_cache')
    cache.delete(BANNERS_CACHE_KEY)


class PaymentMethod(models.Model):
    """Модель типа оплаты"""

    name = models.CharField(max_length=255, verbose_name=_("name"))

    def __str__(self):
        return self.name


class DeliveryMethod(models.Model):
    """
    Модель типа доставки
    Если сумма покупки превышает free_shipping_threshold, стоимость доставки составляет только extra_price,
    иначе - сумма base_price и extra_price
    """

    name = models.CharField(max_length=255, verbose_name=_("name"))
    base_price = models.FloatField(verbose_name=_("base_price"), default=2.0)
    extra_price = models.FloatField(verbose_name=_("extra_price"), default=5.0)
    free_shipping_threshold = models.FloatField(verbose_name=_("free_shipping_threshold"), default=15.0)

    def __str__(self):
        return self.name


class PaymentState(models.Model):
    """Модель статуса оплаты"""

    name = models.CharField(max_length=255, verbose_name=_("name"))

    def __str__(self):
        return self.name


class Order(models.Model):
    """Модель заказа"""

    comment = models.CharField(max_length=255, verbose_name=_("comment"), null=True, blank=True)
    cart = models.OneToOneField('Cart', on_delete=models.CASCADE, verbose_name=_("cart"), null=True)
    customer = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name=_("customer"), related_name="order")
    total_price = models.FloatField(verbose_name=_("total price"))
    date = models.DateTimeField(auto_now=True, verbose_name=_("date"))
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name=_('payment method'),
                                       related_name='order')
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.CASCADE, verbose_name=_('delivery method'),
                                        related_name='order')
    payment_state = models.ForeignKey(PaymentState, on_delete=models.CASCADE, verbose_name=_('payment state'),
                                      related_name='order')
    text_error = models.CharField(max_length=255, verbose_name=_("text_error"), null=True, blank=True)
    city = models.CharField(max_length=255, verbose_name=_("city"), null=True)
    address = models.CharField(max_length=255, verbose_name=_("address"), null=True)
    tm = models.DateTimeField(auto_now_add=True, verbose_name=_("Creation time"))


class Profile(models.Model):
    """Расширенные модели Юзера"""

    user = models.OneToOneField(to=User, on_delete=models.CASCADE, verbose_name=_('user'))
    first_name = models.CharField(max_length=100, verbose_name=_('first name'))
    last_name = models.CharField(max_length=100, verbose_name=_('last name'))
    patronymic = models.CharField(max_length=100, verbose_name=_('patronymic'))
    photo = models.ImageField(upload_to='users_photos/%Y/%m/%d', verbose_name=_('photo'), blank=True,
                              default='icons/user_icon.png', null=True)
    phone = models.CharField(max_length=12, verbose_name=_('phone'), blank=True)
    birth_date = models.DateField(null=True, blank=True, verbose_name=_('birth date'))
    mail = models.EmailField(max_length=100, blank=True, verbose_name=_('mail'))

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return f'{self.user}'

    def get_absolute_url(self):
        return reverse('profile', args=[self.id])


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    logger.debug('Сработал create_profile')
    if created:
        logger.debug(f'Создан Profile для username: {instance.username}')
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    logger.debug('Сработал save_user_profile')
    instance.profile.save()


def import_directory_path(instance, filename):
    return f'imported_files/{filename}'


class ImportFiles(models.Model):
    files = models.FileField(verbose_name=_('File'), upload_to=import_directory_path)
    mail = models.EmailField(max_length=100, verbose_name=_('Mail'), help_text=_(
        '(Enter the mail to which the notification about the end of import will be sent)'))
    status = models.CharField(max_length=100, verbose_name=_('Status'), default='Not started')


class RecentProduct(models.Model):
    """ Модель продуктов из списка просмотренного """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'), related_name='recent_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'))
    tm = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Recent Product')
        verbose_name_plural = _('Recent Products')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.tm}"


class Review(models.Model):
    """Модель отзывов к товарам"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'), related_name='reviews')
    author = models.CharField(verbose_name=_('Author'), max_length=100, null=True)
    email = models.EmailField(verbose_name=_('Email'), null=True)
    text = models.TextField(verbose_name=_('Text'))
    publication_date = models.DateTimeField(auto_now_add=True, verbose_name=_('publication date'))
    is_active = models.BooleanField(verbose_name=_("Is active"), default=True)

    def __str__(self):
        return f'{self.author} added review to {self.product}'

    def get_absolute_url(self):
        return reverse('product', args=[self.product.slug])

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")


class Cart(models.Model):
    """Модель корзины пользователя. Одна запись это информация о продукте от конкретного продавца"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'), related_name='cart')
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Created'), null=True)
    is_payed = models.BooleanField(default=False, verbose_name=_('Is payed'))
    cost = models.FloatField(verbose_name=_('Cost'), default=0)

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")

    def __str__(self):
        return f"Cart of user '{self.user}' for cost {self.cost}"


class CartLine(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name=_('Cart'), related_name='lines')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name=_('Shop'), null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'))
    price = models.FloatField(verbose_name=_("Product price"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantity'))

    class Meta:
        verbose_name = _("Cartline")
        verbose_name_plural = _("Cartlines")

    def __str__(self):
        return f'Пользователь: {self.cart.user} - Продукт:{self.product.name} - Продавец: {self.shop.name} - ' \
               f'Количество:{self.quantity} - Цена(за штуку): {self.price}'

    def is_discounted(self) -> bool:
        """
        Проверка действует ли на позицию скидки
        :return: булево значение проверки
        """
        return True if self.get_active_discounts() else False

    def get_best_discount(self) -> Discount:
        """
        Получение максимальной скидки на позицию
        :return: объект скидки
        """
        logger.debug(f'Получение максимального значения скидки на позицию "{self}"')
        active_discounts = self.get_active_discounts()
        return active_discounts.order_by('-percent')[0]

    def get_active_discounts(self) -> QuerySet[Discount]:
        """
        Получение всех активных скидок на позицию
        :return: набор скидок по запросу
        """
        logger.debug(f'Получение активных скидок на позицию "{self}"')
        active_discounts = Discount.objects.filter(
            (Q(product=self.product, date_end__gt=datetime.now(), date_start__lt=datetime.now())
             | Q(product=self.product, date_end__gt=datetime.now(), date_start__isnull=True))
            & (Q(shop=self.shop) | Q(shop__isnull=True)))
        return active_discounts

    def get_discounted_price(self) -> float:
        """
        Получение цены позиции со скидкой
        :return: значение цены со скидкой
        """
        logger.debug(f'Получение цены позиции "{self}" со скидкой')
        discount = self.get_best_discount()
        return round(self.price * (100 - discount.percent) / 100, 2)
