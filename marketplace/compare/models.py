from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from main.models import Product


class CompareProduct(models.Model):
    """Модель для сравнения товаров"""

    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=_("User"), related_name="compare_products", on_delete=models.CASCADE)
    date_added = models.DateTimeField(verbose_name=_("Date added"), auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.user.username} - {self.date_added}"

    class Meta:
        verbose_name = _("Compare product")
        verbose_name_plural = _("Compare products")


class Characteristic(models.Model):
    """Модель значений зарактеристик"""

    name = models.CharField(max_length=100, verbose_name=_("Characteristic name"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Characteristic")
        verbose_name_plural = _("Characteristics")


class ProductCharacteristic(models.Model):
    """Модель характеристик товаров"""

    product = models.ForeignKey(Product, verbose_name=_("Product"), related_name="characteristics",
                                on_delete=models.CASCADE)
    characteristic = models.ForeignKey(Characteristic, verbose_name=_("Characteristic"), on_delete=models.CASCADE,
                                       related_name="product_characteristics")
    value = models.CharField(max_length=100, verbose_name=_("Characteristic value"))

    def __str__(self):
        return f"{self.product.name} - {self.characteristic.name} - {self.value}"

    class Meta:
        verbose_name = _("Product characteristic")
        verbose_name_plural = _("Product characteristics")
